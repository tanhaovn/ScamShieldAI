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

import jwt
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.db.database import get_db, engine, Base, SessionLocal
from backend.app.db.models import ScanHistory, User, ScamCategory, TrainingDataset, AiModel, ModelEvaluation, SystemActivityLog
from backend.app.ocr.ocr_service import extract_text
from backend.app.risk.risk_engine import analyze_text
from backend.app.visual.visual_forensics import analyze_image_visual

app = FastAPI(title="Vietnamese Scam Detection - Image Module")
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

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ScanImageRequest(BaseModel):
    scam_category_id: int | None = None
    risk_score: int | None = None


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
    email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")

    user = User(
        email=email,
        password_hash=_hash_password(payload.password),
        full_name=payload.full_name or payload.email.split("@")[0],
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_token(user.id)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


@app.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    token = _create_token(user.id)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
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


@app.post("/check-image")
async def check_image(
    file: UploadFile = File(...),
    scam_category_id: int | None = None,
    user_id: int = 1,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    """
    Nhận 1 file ảnh, chạy OCR + phân tích rủi ro, lưu kết quả vào MySQL,
    trả về JSON gồm risk_score, mức độ rủi ro, giải thích và hành động đề xuất.
    """
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.replace("Bearer ", "", 1).strip()
            user_id = int(_decode_token(token))
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

        extracted_text = extract_text(saved_path)
        text_result = analyze_text(extracted_text)

        visual_result = analyze_image_visual(
            saved_path, use_deepfake_model=USE_DEEPFAKE_MODEL
        )
        image_model_result = analyze_phishing_image(saved_path)
        image_model_score = int(image_model_result.probability * 100)

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
            combined_explanation += " Ngoài ra, phân tích hình ảnh phát detect: " + "; ".join(
                visual_result.flags
            )
        if image_model_result.available:
            combined_explanation += " " + image_model_result.explanation

        scan_record = ScanHistory(
            user_id=user_id,
            image_url=f"/uploads/{saved_name}",
            original_filename=file.filename,
            extracted_text=extracted_text,
            scam_category_id=category_id,
            risk_score=combined_score,
            risk_level=combined_level,
            explanation=combined_explanation,
            highlighted_regions={"terms": text_result.highlighted_terms, "visual_flags": visual_result.flags},
            suggested_action=text_result.suggested_action,
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)

        return {
            "scan_id": scan_record.id,
            "image_url": scan_record.image_url,
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
            "scam_category_id": category_id,
        }

    finally:
        pass


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
