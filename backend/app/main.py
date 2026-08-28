"""
FastAPI app cho module kiểm tra hình ảnh.

Chạy thử:
    uvicorn backend.app.main:app --reload

Yêu cầu:
    - MySQL đang chạy, đã import schema.sql
    - File .env cấu hình DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
    - Đã cài tesseract-ocr + tesseract-ocr-vie ở hệ thống (xem app/ocr/ocr_service.py)
"""
import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.db.database import get_db, engine, Base
from backend.app.db.models import ScanHistory
from backend.app.ocr.ocr_service import extract_text
from backend.app.risk.risk_engine import analyze_text
from backend.app.visual.visual_forensics import analyze_image_visual

app = FastAPI(title="Vietnamese Scam Detection - Image Module")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
USE_DEEPFAKE_MODEL = os.getenv("USE_DEEPFAKE_MODEL", "false").lower() == "true"

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse("frontend/index.html")


@app.on_event("startup")
def on_startup():
    # Tạo bảng nếu chưa có (dùng schema.sql là nguồn chuẩn; dòng này chỉ để tiện dev)
    Base.metadata.create_all(bind=engine)


@app.post("/check-image")
async def check_image(
    file: UploadFile = File(...),
    user_id: int = 1,  # TODO: thay bằng user thật lấy từ auth/token
    db: Session = Depends(get_db),
):
    """
    Nhận 1 file ảnh, chạy OCR + phân tích rủi ro, lưu kết quả vào MySQL,
    trả về JSON gồm risk_score, mức độ rủi ro, giải thích và hành động đề xuất.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png...)")

    # Lưu file tạm với tên duy nhất để tránh trùng
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Bước 1: OCR + phân tích văn bản trích được
        extracted_text = extract_text(saved_path)
        text_result = analyze_text(extracted_text)

        # Bước 2: visual forensics (EXIF + ELA + deepfake) chạy trên chính ảnh gốc
        # Chỉ bật model thật qua env sau khi đã kiểm tra torch/torchvision tương thích.
        visual_result = analyze_image_visual(
            saved_path, use_deepfake_model=USE_DEEPFAKE_MODEL
        )
        image_model_result = analyze_phishing_image(saved_path)
        image_model_score = int(image_model_result.probability * 100)

        # Bước 3: kết hợp 2 điểm thành risk score tổng.
        # Công thức đơn giản: lấy điểm cao hơn làm nền, cộng thêm 30% điểm còn lại,
        # tránh trường hợp cộng dồn thẳng làm risk score vượt quá thực tế.
        component_scores = [text_result.risk_score, visual_result.visual_score]
        if image_model_result.available:
            component_scores.append(image_model_score)
        combined_score = max(component_scores) + int(0.3 * min(component_scores))
        combined_score = min(combined_score, 100)

        if combined_score >= 60:
            combined_level = "nguy_hiem"
        elif combined_score >= 25:
            combined_level = "nghi_ngo"
        else:
            combined_level = "an_toan"

        combined_explanation = text_result.explanation
        if visual_result.flags:
            combined_explanation += " Ngoài ra, phân tích hình ảnh phát hiện: " + "; ".join(
                visual_result.flags
            )
        if image_model_result.available:
            combined_explanation += " " + image_model_result.explanation

        scan_record = ScanHistory(
            user_id=user_id,
            input_type="image",
            original_filename=file.filename,
            extracted_text=extracted_text,
            risk_score=combined_score,
            text_risk_score=text_result.risk_score,
            visual_risk_score=visual_result.visual_score,
            risk_level=combined_level,
            scam_type=text_result.scam_type,
            explanation=combined_explanation,
            highlighted_terms=text_result.highlighted_terms,
            visual_flags=visual_result.flags,
            suggested_action=text_result.suggested_action,
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)

        return {
            "scan_id": scan_record.id,
            "extracted_text": extracted_text,
            "risk_score": combined_score,
            "risk_level": combined_level,
            "text_risk_score": text_result.risk_score,
            "visual_risk_score": visual_result.visual_score,
            "image_model_available": image_model_result.available,
            "image_model_label": image_model_result.label,
            "image_model_score": image_model_score,
            "scam_type": text_result.scam_type,
            "highlighted_terms": text_result.highlighted_terms,
            "visual_flags": visual_result.flags,
            "explanation": combined_explanation,
            "suggested_action": text_result.suggested_action,
        }

    finally:
        # dọn file tạm sau khi xử lý xong (bỏ dòng này nếu muốn giữ lại ảnh gốc)
        if os.path.exists(saved_path):
            os.remove(saved_path)


@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    """Lấy lịch sử kiểm tra của 1 user, mới nhất trước."""
    records = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == user_id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    return [
        {
            "scan_id": r.id,
            "input_type": r.input_type,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "scam_type": r.scam_type,
            "created_at": r.created_at,
        }
        for r in records
    ]


@app.get("/health")
def health_check():
    return {"status": "ok"}
