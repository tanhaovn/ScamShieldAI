import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from backend.app.ai.phishvn_url_model import extract_url_candidates
from backend.app.ai.gemini_explainer import explain_scan_result
from backend.app.api.dependencies import get_optional_current_user
from backend.app.core.config import UPLOAD_DIR
from backend.app.db.database import get_db
from backend.app.db.models import ScamCategory, User
from backend.app.document.pdf_service import extract_pdf_content
from backend.app.ocr.highlight_service import build_suspicious_regions
from backend.app.ocr.ocr_service import extract_text_and_boxes, get_image_dimensions
from backend.app.schemas.scan import BatchUrlRequest, ExplanationFollowupRequest, TextCheckRequest, UrlCheckRequest
from backend.app.services.analysis import analyze_content_payload, local_analysis_response
from backend.app.services.history import account_analysis_response, save_scan_history
from backend.app.visual.qr_analysis import decode_qr_codes


router = APIRouter(tags=["Scanning"])


@router.post("/explain-result")
def explain_result(payload: ExplanationFollowupRequest):
    context = {
        "risk_score": payload.risk_score,
        "risk_level": payload.risk_level,
        "source_type": payload.source_type,
        "existing_explanation": payload.explanation,
        "evidence": [item.model_dump() for item in payload.evidence],
        "analyzed_text_excerpt": payload.extracted_text,
    }
    try:
        answer, model = explain_scan_result(
            question=payload.question.strip(),
            context=context,
            language=payload.language,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"answer": answer, "model": model}


@router.post("/check-text")
def check_text(
    payload: TextCheckRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    content = payload.text.strip()
    analysis = analyze_content_payload(content)
    filename = "Nội dung tin nhắn"
    if current_user:
        row = save_scan_history(
            db, current_user, analysis,
            source_type="text", original_filename=filename,
        )
        return account_analysis_response(
            analysis, row, source_type="text", original_filename=filename
        )
    return local_analysis_response(analysis, "text", filename)


@router.post("/check-url")
def check_url(
    payload: UrlCheckRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    url = payload.url.strip()
    if not extract_url_candidates(url):
        raise HTTPException(
            status_code=422,
            detail="URL không hợp lệ. Ví dụ đúng: https://example.com/login",
        )
    analysis = analyze_content_payload(url)
    filename = url[:180]
    if current_user:
        row = save_scan_history(
            db, current_user, analysis,
            source_type="url", original_filename=filename,
        )
        return account_analysis_response(
            analysis, row, source_type="url", original_filename=filename
        )
    return local_analysis_response(analysis, "url", filename)


@router.post("/check-urls-batch")
def check_urls_batch(
    payload: BatchUrlRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    unique_urls = list(
        dict.fromkeys(value.strip() for value in payload.urls if value.strip())
    )[:50]
    results = []
    for url in unique_urls:
        if not extract_url_candidates(url):
            results.append(
                {
                    "url": url,
                    "status": "invalid",
                    "risk_score": 0,
                    "risk_level": "unknown",
                }
            )
            continue
        analysis = analyze_content_payload(url)
        scan_id = None
        if current_user:
            row = save_scan_history(
                db, current_user, analysis,
                source_type="url", original_filename=url[:180],
            )
            scan_id = row.id
        results.append({
            "url": url,
            "status": "checked",
            "scan_id": scan_id,
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "domain_intelligence": analysis["domain_intelligence"],
            "google_safe_browsing": analysis["google_safe_browsing"],
        })
    return {"total": len(results), "results": results}


@router.post("/check-document")
async def check_document(
    file: UploadFile = File(...),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    filename = file.filename or "document.pdf"
    if file.content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Tài liệu phải là file PDF")

    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"
    try:
        with saved_path.open("wb") as buffer:
            received_size = 0
            while chunk := await file.read(1024 * 1024):
                received_size += len(chunk)
                if received_size > 15 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="PDF tối đa 15 MB")
                buffer.write(chunk)

        try:
            document = extract_pdf_content(str(saved_path), max_pages=10)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        content = document["text"]
        if not content and not document["qr_codes"]:
            raise HTTPException(
                status_code=422,
                detail="Không đọc được chữ hoặc mã QR trong PDF",
            )

        analysis = analyze_content_payload(content, qr_codes=document["qr_codes"])
        if current_user:
            row = save_scan_history(
                db, current_user, analysis,
                source_type="pdf",
                original_filename=filename,
                extra_details={"document_info": {
                    "page_count": document["page_count"],
                    "processed_pages": document["processed_pages"],
                    "truncated": document["truncated"],
                }},
            )
            response = account_analysis_response(
                analysis, row, source_type="pdf", original_filename=filename
            )
        else:
            response = local_analysis_response(analysis, "pdf", filename)
        response["document_info"] = {
            "page_count": document["page_count"],
            "processed_pages": document["processed_pages"],
            "truncated": document["truncated"],
        }
        return response
    finally:
        saved_path.unlink(missing_ok=True)


@router.post("/check-image")
async def check_image(
    file: UploadFile = File(...),
    scam_category_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Run the complete image pipeline for guests or authenticated admins."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png...)")

    upload_id = uuid.uuid4().hex
    saved_name = ""
    saved_path = UPLOAD_DIR / f"{upload_id}.upload"
    completed_scan = False

    try:
        received_size = 0
        with saved_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                received_size += len(chunk)
                if received_size > 10 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="Ảnh tối đa 10 MB")
                buffer.write(chunk)
        try:
            with Image.open(saved_path) as image:
                image.verify()
            with Image.open(saved_path) as image:
                width, height = image.size
                image_format = (image.format or "").upper()
            extension = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}.get(
                image_format
            )
            if not extension:
                raise HTTPException(
                    status_code=400,
                    detail="Chỉ hỗ trợ ảnh JPEG, PNG hoặc WEBP",
                )
            if width < 16 or height < 16 or width * height > 25_000_000:
                raise HTTPException(
                    status_code=400,
                    detail="Kích thước ảnh không hợp lệ hoặc vượt quá 25 megapixel",
                )
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail="File không phải ảnh hợp lệ hoặc đã bị hỏng",
            ) from exc
        final_path = UPLOAD_DIR / f"{upload_id}{extension}"
        saved_path.replace(final_path)
        saved_path = final_path
        saved_name = final_path.name

        category_id = scam_category_id
        if category_id is None:
            category = db.query(ScamCategory).filter(
                ScamCategory.code == "phishing_screenshot"
            ).first()
            category_id = category.id if category else None

        with ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="image-read",
        ) as executor:
            ocr_future = executor.submit(extract_text_and_boxes, saved_path)
            qr_future = executor.submit(decode_qr_codes, saved_path)
            extracted_text, ocr_words = ocr_future.result()
            qr_codes = qr_future.result()

        analysis = analyze_content_payload(
            extracted_text,
            image_path=saved_path,
            qr_codes=qr_codes,
        )
        image_dimensions = get_image_dimensions(saved_path)
        suspicious_urls = [
            item.get("url") or item.get("normalized_url")
            for item in analysis["phishvn_urls"]
            if int(item.get("risk_score") or 0) >= 25
            and (item.get("url") or item.get("normalized_url"))
        ]
        image_annotations = build_suspicious_regions(
            ocr_words,
            analysis["highlighted_terms"],
            suspicious_urls,
        )

        scan_id = None
        created_at = datetime.now(timezone.utc)
        if current_user:
            scan_record = save_scan_history(
                db,
                current_user,
                analysis,
                source_type="image",
                original_filename=file.filename or "Ảnh kiểm tra",
                image_url=f"/uploads/{saved_name}",
                scam_category_id=category_id,
                extra_details={
                    "image_annotations": image_annotations,
                    "image_dimensions": image_dimensions,
                },
            )
            scan_id = scan_record.id
            created_at = scan_record.created_at or created_at

        response = {
            **analysis,
            "scan_id": scan_id,
            "image_url": f"/uploads/{saved_name}",
            "original_filename": file.filename,
            "created_at": created_at.isoformat(),
            "storage": "database" if current_user else "local_storage",
            "source_type": "image",
            "scam_category_id": category_id,
            "image_annotations": image_annotations,
            "image_dimensions": image_dimensions,
        }
        completed_scan = True
        return response
    finally:
        if not completed_scan:
            Path(saved_path).unlink(missing_ok=True)
            Path(saved_path).with_name(
                f"{Path(saved_path).stem}.gradcam.jpg"
            ).unlink(missing_ok=True)
