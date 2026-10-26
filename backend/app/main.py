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
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import jwt
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.ai.phishvn_url_model import analyze_urls_in_text, extract_url_candidates
from backend.app.ai.vlm_image_analyzer import analyze_image_context
from backend.app.db.database import get_db, engine, Base, SessionLocal
from backend.app.db.models import AuthIdentity, ScanHistory, User, ScamCategory, TrainingDataset, AiModel, ModelEvaluation, SystemActivityLog
from backend.app.document.pdf_service import extract_pdf_content
from backend.app.ocr.highlight_service import build_suspicious_regions
from backend.app.ocr.ocr_service import extract_text_and_boxes, get_image_dimensions
from backend.app.risk.explanation_builder import build_analysis_explanation
from backend.app.risk.risk_engine import analyze_text
from backend.app.risk.safety_assistant import answer_safety_question
from backend.app.visual.visual_forensics import analyze_image_visual
from backend.app.visual.qr_analysis import decode_qr_codes

app = FastAPI(title="Vietnamese Scam Detection - Multi-source Scanner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend-react"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
USE_DEEPFAKE_MODEL = os.getenv("USE_DEEPFAKE_MODEL", "false").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str = Field(min_length=20)


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)


class ScanImageRequest(BaseModel):
    scam_category_id: int | None = None
    risk_score: int | None = None


class TextCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


class UrlCheckRequest(BaseModel):
    url: str = Field(min_length=3, max_length=4096)


class AssistantQuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    risk_level: str = Field(max_length=30)
    risk_score: int = Field(ge=0, le=100)
    highlighted_terms: list[str] = Field(default_factory=list, max_length=30)
    urls: list[dict] = Field(default_factory=list, max_length=20)
    suggested_action: str = Field(default="", max_length=3000)
    verdict: str = Field(default="", max_length=3000)


class TrainingDatasetRequest(BaseModel):
    image_url: str
    scam_category_id: int | None = None
    is_anonymized: bool = False
    is_verified: bool = False


class AiModelRequest(BaseModel):
    version_name: str
    description: str | None = None
    is_active: bool = False


class SystemLogRequest(BaseModel):
    action_type: str
    description: str | None = None


class ModelEvaluationRequest(BaseModel):
    ai_model_id: int
    macro_f1: float | None = None
    recall: float | None = None
    false_alarm_rate: float | None = None
    explanation_usefulness: float | None = None


def _hash_password(password: str) -> str:
    import hashlib
    import secrets

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2_sha256$100000${salt}${digest.hex()}"


def _verify_password(password: str, password_hash: str) -> bool:
    import hashlib
    import hmac

    try:
        algorithm, iterations, salt, expected = password_hash.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    )
    return hmac.compare_digest(derived.hex(), expected)


def _create_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> int:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return int(payload["sub"])


def _auth_response(user: User) -> dict:
    return {
        "token": _create_token(user.id),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu token xác thực")

    token = authorization.replace("Bearer ", "", 1).strip()
    try:
        user_id = _decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return user


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


def seed_default_categories(db: Session):
    default_categories = [
        ("phishing_screenshot", "Phishing Screenshot", "Ảnh chụp màn hình lừa đảo"),
        ("fake_invoice", "Fake Invoice", "Hóa đơn giả mạo"),
        ("impersonation", "Impersonation", "Lừa gạt danh tính"),
        ("sms_scam", "SMS Scam", "Lừa đảo qua tin nhắn"),
        ("payment_redirect", "Payment Redirect", "Chuyển hướng thanh toán giả"),
    ]

    for code, display_name, description in default_categories:
        existing = db.query(ScamCategory).filter(ScamCategory.code == code).first()
        if not existing:
            db.add(ScamCategory(code=code, display_name=display_name, description=description))

    admin_email = "admin@scamdetector.local"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        db.add(
            User(
                email=admin_email,
                password_hash=_hash_password("Admin@123"),
                full_name="System Admin",
                role="admin",
                is_active=True,
            )
        )

    db.commit()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()


@app.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=403,
        detail=(
            "Ứng dụng đang dùng chế độ khách, không cần đăng ký tài khoản. "
            "Chỉ quản trị viên mới đăng nhập."
        ),
    )


@app.post("/admin/login")
@app.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Chỉ tài khoản quản trị viên mới được đăng nhập",
        )

    return _auth_response(user)


@app.post("/auth/google")
def authenticate_with_google(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="Google Sign-In chưa được cấu hình trên máy chủ",
        )

    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Máy chủ chưa cài thư viện google-auth",
        ) from exc

    try:
        identity_data = google_id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Google ID token không hợp lệ") from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Không thể xác minh tài khoản Google lúc này",
        ) from exc

    subject = str(identity_data.get("sub") or "").strip()
    email = str(identity_data.get("email") or "").strip().lower()
    email_verified = identity_data.get("email_verified") in {True, "true"}
    if not subject or not email or not email_verified:
        raise HTTPException(
            status_code=401,
            detail="Tài khoản Google chưa xác minh email",
        )

    identity = (
        db.query(AuthIdentity)
        .filter(
            AuthIdentity.provider == "google",
            AuthIdentity.provider_subject == subject,
        )
        .first()
    )
    if not identity or identity.user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Chỉ tài khoản Google đã liên kết với quản trị viên mới được đăng nhập",
        )

    user = identity.user

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")

    return _auth_response(user)


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "auth_provider": (
            current_user.auth_identities[0].provider
            if current_user.auth_identities
            else "password"
        ),
    }


@app.patch("/me")
def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    full_name = " ".join(payload.full_name.strip().split())
    if len(full_name) < 2:
        raise HTTPException(status_code=400, detail="Tên hiển thị phải có ít nhất 2 ký tự")

    current_user.full_name = full_name
    db.commit()
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "auth_provider": (
            current_user.auth_identities[0].provider
            if current_user.auth_identities
            else "password"
        ),
    }


@app.get("/scam-categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(ScamCategory).order_by(ScamCategory.id.asc()).all()
    return [
        {
            "id": item.id,
            "code": item.code,
            "display_name": item.display_name,
            "description": item.description,
        }
        for item in categories
    ]


@app.get("/scan-history")
def list_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == current_user.id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    return [
        {
            "id": row.id,
            "image_url": row.image_url,
            "original_filename": row.original_filename,
            "risk_score": row.risk_score,
            "risk_level": row.risk_level,
            "scam_category_id": row.scam_category_id,
            "extracted_text": row.extracted_text,
            "explanation": row.explanation,
            "suggested_action": row.suggested_action,
            "highlighted_regions": row.highlighted_regions,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.get("/training-dataset")
def list_training_dataset(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(TrainingDataset)
    if current_user.role != "admin":
        query = query.filter(TrainingDataset.uploaded_by == current_user.id)

    rows = query.order_by(TrainingDataset.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "image_url": row.image_url,
            "scam_category_id": row.scam_category_id,
            "is_anonymized": row.is_anonymized,
            "is_verified": row.is_verified,
            "uploaded_by": row.uploaded_by,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.get("/model-evaluations")
def list_model_evaluations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem đánh giá model")

    rows = db.query(ModelEvaluation).order_by(ModelEvaluation.evaluated_at.desc()).all()
    return [
        {
            "id": row.id,
            "ai_model_id": row.ai_model_id,
            "macro_f1": row.macro_f1,
            "recall": row.recall,
            "false_alarm_rate": row.false_alarm_rate,
            "explanation_usefulness": row.explanation_usefulness,
            "evaluated_at": row.evaluated_at,
        }
        for row in rows
    ]


@app.get("/system-logs")
def list_system_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem log hệ thống")

    rows = db.query(SystemActivityLog).order_by(SystemActivityLog.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "admin_id": row.admin_id,
            "action_type": row.action_type,
            "description": row.description,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def _analyze_content_payload(
    content: str,
    *,
    image_path: str | None = None,
    qr_codes: list[str] | None = None,
) -> dict:
    """Run the shared text, URL and optional visual pipeline."""
    qr_codes = qr_codes or []
    analysis_text = "\n".join(part for part in [content.strip(), *qr_codes] if part).strip()
    text_result = analyze_text(analysis_text)
    phishvn_result = analyze_urls_in_text(analysis_text)

    if image_path:
        visual_result = analyze_image_visual(
            image_path, use_deepfake_model=USE_DEEPFAKE_MODEL
        )
        image_model_result = analyze_phishing_image(image_path)
        image_model_score = int(image_model_result.probability * 100)
        vlm_result = analyze_image_context(
            image_path,
            ocr_text=analysis_text,
            qr_codes=qr_codes,
            visual_flags=visual_result.flags,
            image_model_probability=image_model_result.probability if image_model_result.available else None,
            phishvn_url_score=int(phishvn_result.risk_score),
            phishvn_predictions=phishvn_result.predictions_as_dicts() if hasattr(phishvn_result, "predictions_as_dicts") else [],
        )
    else:
        visual_result = SimpleNamespace(visual_score=0, flags=[])
        image_model_result = SimpleNamespace(
            available=False,
            probability=0.0,
            label="not_applicable",
            explanation="Không áp dụng model hình ảnh cho nguồn dữ liệu này.",
        )
        image_model_score = 0
        vlm_result = SimpleNamespace(
            available=False,
            risk_score=0,
            verdict="not_applicable",
            confidence=0.0,
            risk_indicators=[],
            observed_text=[],
            reasoning="",
            recommended_action="",
            model_name="Qwen2.5-VL",
            note="Không áp dụng phân tích ngữ cảnh ảnh cho nguồn dữ liệu này.",
        )

    component_scores = [int(text_result.risk_score)]
    if phishvn_result.available and phishvn_result.predictions:
        component_scores.append(int(phishvn_result.risk_score))
    if image_path:
        component_scores.append(int(visual_result.visual_score))
        if image_model_result.available:
            component_scores.append(image_model_score)
        if vlm_result.available:
            component_scores.append(int(vlm_result.risk_score))

    if image_path and vlm_result.available:
        if vlm_result.verdict == "safe":
            combined_score = min(int(vlm_result.risk_score), 20)
        else:
            combined_score = max(
                int(vlm_result.risk_score),
                int(text_result.risk_score),
                int(phishvn_result.risk_score) if phishvn_result.available else 0,
            )
            if len(component_scores) > 1 and min(component_scores) > 0:
                combined_score += int(0.2 * min(component_scores))
    else:
        combined_score = max(component_scores)
        if len(component_scores) > 1 and min(component_scores) > 0:
            combined_score += int(0.2 * min(component_scores))
    combined_score = min(combined_score, 100)

    if combined_score >= 60:
        combined_level = "nguy_hiem"
    elif combined_score >= 25:
        combined_level = "nghi_ngo"
    else:
        combined_level = "an_toan"

    combined_scam_type = text_result.scam_type
    if phishvn_result.risk_score >= 50 and phishvn_result.risk_score >= text_result.risk_score:
        combined_scam_type = "phishing_url"

    suggested_action = text_result.suggested_action
    if phishvn_result.risk_score >= 60:
        suggested_action = (
            "KHÔNG mở URL, KHÔNG đăng nhập hoặc cung cấp OTP/thông tin thanh toán. "
            "Hãy tự nhập địa chỉ website chính thức hoặc liên hệ tổ chức qua kênh đã xác minh."
        )
    elif phishvn_result.risk_score >= 25 and text_result.risk_score < 25:
        suggested_action = (
            "URL có dấu hiệu cần kiểm tra thêm. Không bấm trực tiếp; hãy đối chiếu tên miền "
            "với website chính thức trước khi tiếp tục."
        )

    combined_explanation, analysis_breakdown = build_analysis_explanation(
        extracted_text=analysis_text,
        text_result=text_result,
        phishvn_result=phishvn_result,
        visual_result=visual_result,
        image_model_result=image_model_result,
        image_model_score=image_model_score,
        vlm_result=vlm_result,
        combined_score=combined_score,
        combined_level=combined_level,
        include_visual=bool(image_path),
    )

    return {
        "extracted_text": content,
        "risk_score": combined_score,
        "risk_level": combined_level,
        "text_risk_score": text_result.risk_score,
        "phishvn_available": phishvn_result.available,
        "phishvn_model": phishvn_result.model_name,
        "phishvn_url_risk_score": phishvn_result.risk_score,
        "phishvn_urls": phishvn_result.predictions_as_dicts(),
        "visual_risk_score": visual_result.visual_score,
        "image_model_available": image_model_result.available,
        "image_model_label": image_model_result.label,
        "image_model_score": image_model_score,
        "vlm_analysis": vlm_result.to_dict() if hasattr(vlm_result, "to_dict") else vars(vlm_result),
        "scam_type": combined_scam_type,
        "highlighted_terms": text_result.highlighted_terms,
        "visual_flags": visual_result.flags,
        "qr_codes": qr_codes,
        "explanation": combined_explanation,
        "analysis_breakdown": analysis_breakdown,
        "suggested_action": suggested_action,
    }


def _local_analysis_response(payload: dict, source_type: str, filename: str) -> dict:
    return {
        **payload,
        "scan_id": None,
        "image_url": "",
        "original_filename": filename,
        "created_at": datetime.utcnow().isoformat(),
        "storage": "local_storage",
        "source_type": source_type,
        "scam_category_id": None,
    }


@app.post("/check-text")
def check_text(payload: TextCheckRequest):
    content = payload.text.strip()
    return _local_analysis_response(
        _analyze_content_payload(content),
        "text",
        "Nội dung tin nhắn",
    )


@app.post("/check-url")
def check_url(payload: UrlCheckRequest):
    url = payload.url.strip()
    if not extract_url_candidates(url):
        raise HTTPException(
            status_code=422,
            detail="URL không hợp lệ. Ví dụ đúng: https://example.com/login",
        )
    return _local_analysis_response(
        _analyze_content_payload(url),
        "url",
        url[:180],
    )


@app.post("/analysis-assistant")
def analysis_assistant(payload: AssistantQuestionRequest):
    """Answer follow-up safety questions using only the completed scan evidence."""
    return {
        "answer": answer_safety_question(
            question=payload.question,
            risk_level=payload.risk_level,
            risk_score=payload.risk_score,
            highlighted_terms=payload.highlighted_terms,
            urls=payload.urls,
            suggested_action=payload.suggested_action,
            verdict=payload.verdict,
        )
    }


@app.post("/check-document")
async def check_document(file: UploadFile = File(...)):
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

        response = _local_analysis_response(
            _analyze_content_payload(content, qr_codes=document["qr_codes"]),
            "pdf",
            filename,
        )
        response["document_info"] = {
            "page_count": document["page_count"],
            "processed_pages": document["processed_pages"],
            "truncated": document["truncated"],
        }
        return response
    finally:
        saved_path.unlink(missing_ok=True)


@app.post("/check-image")
async def check_image(
    file: UploadFile = File(...),
    scam_category_id: int | None = None,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    """
    Nhận ảnh và chạy đầy đủ pipeline phân tích.

    Khách không cần đăng nhập và tự lưu lịch sử bằng localStorage ở frontend.
    Chỉ lượt quét của admin đã xác thực mới được ghi vào MySQL.
    """
    admin_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.replace("Bearer ", "", 1).strip()
            authenticated_user = db.query(User).filter(User.id == int(_decode_token(token))).first()
            if authenticated_user and authenticated_user.role == "admin" and authenticated_user.is_active:
                admin_user = authenticated_user
        except Exception:
            pass

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png...)")

    ext = os.path.splitext(file.filename)[1] or ".jpg"
    saved_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        category_id = scam_category_id
        if category_id is None:
            category = db.query(ScamCategory).filter(ScamCategory.code == "phishing_screenshot").first()
            category_id = category.id if category else None

        extracted_text, ocr_words = extract_text_and_boxes(saved_path)
        qr_codes = decode_qr_codes(saved_path)
        analysis = _analyze_content_payload(
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
        created_at = datetime.utcnow()
        if admin_user:
            scan_record = ScanHistory(
                user_id=admin_user.id,
                image_url=f"/uploads/{saved_name}",
                original_filename=file.filename,
                extracted_text=extracted_text,
                scam_category_id=category_id,
                risk_score=analysis["risk_score"],
                risk_level=analysis["risk_level"],
                explanation=analysis["explanation"],
                highlighted_regions={
                    "terms": analysis["highlighted_terms"],
                    "visual_flags": analysis["visual_flags"],
                    "phishvn_urls": analysis["phishvn_urls"],
                    "qr_codes": qr_codes,
                    "image_annotations": image_annotations,
                    "image_dimensions": image_dimensions,
                    "analysis_breakdown": analysis["analysis_breakdown"],
                },
                suggested_action=analysis["suggested_action"],
            )
            db.add(scan_record)
            db.commit()
            db.refresh(scan_record)
            scan_id = scan_record.id
            created_at = scan_record.created_at or created_at

        return {
            **analysis,
            "scan_id": scan_id,
            "image_url": f"/uploads/{saved_name}",
            "original_filename": file.filename,
            "created_at": created_at.isoformat(),
            "storage": "database" if admin_user else "local_storage",
            "source_type": "image",
            "scam_category_id": category_id,
            "image_annotations": image_annotations,
            "image_dimensions": image_dimensions,
        }

    finally:
        pass


@app.get("/history/{user_id}")
def get_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy lịch sử máy chủ; chỉ quản trị viên đã xác thực được truy cập."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem lịch sử máy chủ")
    records = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == user_id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    return [
        {
            "scan_id": r.id,
            "image_url": r.image_url,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "scam_category_id": r.scam_category_id,
            "created_at": r.created_at,
        }
        for r in records
    ]


@app.post("/training-dataset")
def create_training_dataset(
    payload: TrainingDatasetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được upload dataset huấn luyện")

    dataset = TrainingDataset(
        image_url=payload.image_url,
        scam_category_id=payload.scam_category_id,
        is_anonymized=payload.is_anonymized,
        is_verified=payload.is_verified,
        uploaded_by=current_user.id,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return {"id": dataset.id, "image_url": dataset.image_url}


@app.get("/ai-models")
def list_ai_models(db: Session = Depends(get_db)):
    return [
        {
            "id": item.id,
            "version_name": item.version_name,
            "description": item.description,
            "is_active": item.is_active,
            "created_at": item.created_at,
        }
        for item in db.query(AiModel).order_by(AiModel.created_at.desc()).all()
    ]


@app.post("/ai-models")
def create_ai_model(
    payload: AiModelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được quản lý model")

    model = AiModel(
        version_name=payload.version_name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return {"id": model.id, "version_name": model.version_name}


@app.post("/model-evaluations")
def create_model_evaluation(
    payload: ModelEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được ghi đánh giá model")

    evaluation = ModelEvaluation(
        ai_model_id=payload.ai_model_id,
        macro_f1=payload.macro_f1,
        recall=payload.recall,
        false_alarm_rate=payload.false_alarm_rate,
        explanation_usefulness=payload.explanation_usefulness,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return {"id": evaluation.id}


@app.post("/system-logs")
def create_system_log(
    payload: SystemLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được ghi log hệ thống")

    log = SystemActivityLog(
        admin_id=current_user.id,
        action_type=payload.action_type,
        description=payload.description,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"id": log.id, "action_type": log.action_type}


@app.get("/health")
def health_check():
    return {"status": "ok"}
