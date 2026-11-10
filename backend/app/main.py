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
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import jwt
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.ai.phishvn_url_model import analyze_urls_in_text, extract_url_candidates
from backend.app.ai.google_safe_browsing import check_urls as check_google_safe_browsing
from backend.app.ai.domain_intelligence import inspect_urls
from backend.app.ai.vlm_image_analyzer import analyze_image_context
from backend.app.db.database import get_db, engine, Base, SessionLocal
from backend.app.db.models import AuthIdentity, ScanHistory, User, ScamCategory, TrainingDataset, AiModel, ModelEvaluation, SystemActivityLog, ScanFeedback, ScamKeyword
from backend.app.document.pdf_service import extract_pdf_content
from backend.app.ocr.highlight_service import build_suspicious_regions
from backend.app.ocr.ocr_service import extract_text_and_boxes, get_image_dimensions
from backend.app.risk.explanation_builder import build_analysis_explanation
from backend.app.risk.risk_engine import analyze_text
from backend.app.risk.safety_assistant import answer_safety_question
from backend.app.visual.visual_forensics import analyze_image_visual
from backend.app.visual.qr_analysis import decode_qr_codes
from backend.app.evaluation.benchmark import run_detector_benchmark

app = FastAPI(title="Vietnamese Scam Detection - Multi-source Scanner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
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
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
if APP_ENV == "production" and JWT_SECRET == "dev-secret-key-change-me":
    raise RuntimeError("JWT_SECRET bắt buộc phải được cấu hình an toàn trong production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
APP_VERSION = os.getenv("APP_VERSION", "1.2.0").strip() or "1.2.0"
STARTED_AT = datetime.now(timezone.utc)


def _read_git_commit() -> str:
    """Resolve a short revision without invoking Git in a request handler."""
    configured = os.getenv("GIT_COMMIT", "").strip()
    if configured:
        return configured[:12]
    try:
        git_dir = PROJECT_ROOT / ".git"
        if git_dir.is_file():
            target = git_dir.read_text(encoding="utf-8").strip().removeprefix("gitdir: ")
            git_dir = (PROJECT_ROOT / target).resolve()
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref: "):
            return head[:12]
        ref_name = head.removeprefix("ref: ")
        ref_file = git_dir / ref_name
        if ref_file.exists():
            return ref_file.read_text(encoding="utf-8").strip()[:12]
        packed = git_dir / "packed-refs"
        if packed.exists():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.endswith(f" {ref_name}"):
                    return line.split(" ", 1)[0][:12]
    except (OSError, ValueError):
        pass
    return "unknown"


GIT_COMMIT = _read_git_commit()


def _runtime_info() -> dict:
    return {
        "status": "ok",
        "app_version": APP_VERSION,
        "git_commit": GIT_COMMIT,
        "environment": APP_ENV,
        "started_at": STARTED_AT.isoformat(),
        "services": {
            "database": engine.url.get_backend_name(),
            "image_model": (PROJECT_ROOT / "models" / "phishing_resnet18.pt").exists(),
            "url_model": (PROJECT_ROOT / "models" / "phishvn_url_histgb.joblib").exists(),
            "safe_browsing": bool(os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()),
        },
    }

dist_dir = FRONTEND_DIR / "dist"
if (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")
app.mount("/static", StaticFiles(directory=dist_dir if dist_dir.exists() else FRONTEND_DIR), name="static")
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


class BatchUrlRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=50)


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


class ScanFeedbackRequest(BaseModel):
    scan_id: int | None = None
    client_scan_id: str | None = Field(default=None, max_length=100)
    verdict: str = Field(pattern="^(correct|false_alarm|missed_scam)$")
    predicted_level: str = Field(max_length=30)
    risk_score: int = Field(ge=0, le=100)
    source_type: str = Field(max_length=30)
    original_filename: str | None = Field(default=None, max_length=512)
    note: str | None = Field(default=None, max_length=1000)
    highlighted_terms: list[str] = Field(default_factory=list, max_length=30)
    urls: list[str] = Field(default_factory=list, max_length=20)


class ScamKeywordRequest(BaseModel):
    keyword: str = Field(min_length=2, max_length=255)
    category: str = Field(min_length=2, max_length=100)
    weight: int = Field(ge=1, le=50)


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
    dist_index = FRONTEND_DIR / "dist" / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
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


@app.get("/scam-keywords")
def list_scam_keywords(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem từ khóa")
    return [{"id": row.id, "keyword": row.keyword, "category": row.category, "weight": row.weight, "created_at": row.created_at} for row in db.query(ScamKeyword).order_by(ScamKeyword.category, ScamKeyword.weight.desc()).all()]


@app.post("/scam-keywords", status_code=201)
def create_scam_keyword(payload: ScamKeywordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới quản lý từ khóa")
    keyword = payload.keyword.strip().lower()
    if db.query(ScamKeyword).filter(ScamKeyword.keyword == keyword).first():
        raise HTTPException(status_code=409, detail="Từ khóa đã tồn tại")
    row = ScamKeyword(keyword=keyword, category=payload.category.strip(), weight=payload.weight)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "keyword": row.keyword, "category": row.category, "weight": row.weight}


def _analyze_content_payload(
    content: str,
    *,
    image_path: str | None = None,
    qr_codes: list[str] | None = None,
) -> dict:
    """Run the shared text, URL and optional visual pipeline."""
    qr_codes = qr_codes or []
    analysis_text = "\n".join(part for part in [content.strip(), *qr_codes] if part).strip()
    url_candidates = extract_url_candidates(analysis_text)
    domain_intelligence = inspect_urls(url_candidates)

    # Only the remote reputation lookup is overlapped with local inference.
    # Running several native ML runtimes (Torch/OpenMP/OpenCV) concurrently can
    # oversubscribe CPUs or stall on Windows, so the accuracy-critical local
    # models intentionally remain sequential and deterministic.
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="reputation") as executor:
        safe_browsing_future = executor.submit(
            check_google_safe_browsing,
            url_candidates,
        )
        text_result = analyze_text(analysis_text)
        phishvn_result = analyze_urls_in_text(analysis_text)
        if image_path:
            visual_result = analyze_image_visual(
                image_path, use_deepfake_model=USE_DEEPFAKE_MODEL
            )
            image_model_result = analyze_phishing_image(image_path)
        safe_browsing_result = safe_browsing_future.result()

    domain_score = max((int(item.get("score") or 0) for item in domain_intelligence), default=0)
    trusted_domains_only = bool(domain_intelligence) and all(bool(item.get("trusted")) for item in domain_intelligence)
    raw_phishvn_score = int(phishvn_result.risk_score)
    calibrated_phishvn_score = raw_phishvn_score
    if trusted_domains_only and int(text_result.risk_score) < 25 and not safe_browsing_result.matches:
        # An auditable exact-domain registry may suppress an isolated model
        # false positive, but never a threat-list match or risky message text.
        calibrated_phishvn_score = 0
    elif raw_phishvn_score >= 60 and domain_score < 50 and int(text_result.risk_score) < 25 and not safe_browsing_result.matches:
        # One uncorroborated URL model is enough to request review, not enough
        # to assert danger. This model is known to be overconfident OOD.
        calibrated_phishvn_score = 45

    if image_path:
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
        component_scores.append(calibrated_phishvn_score)
    if domain_score:
        component_scores.append(domain_score)
    if safe_browsing_result.matches:
        component_scores.append(int(safe_browsing_result.risk_score))
    if image_path:
        component_scores.append(int(visual_result.visual_score))
        if image_model_result.available:
            component_scores.append(image_model_score)
        if vlm_result.available:
            component_scores.append(int(vlm_result.risk_score))

    # ---------------------------------------------------------
    # Calibrated Multimodal Consensus Fusion (Soft Voting)
    # ---------------------------------------------------------
    primary_scores = [int(text_result.risk_score)]
    if phishvn_result.available and phishvn_result.predictions and calibrated_phishvn_score:
        primary_scores.append(calibrated_phishvn_score)
    if domain_score >= 20:
        primary_scores.append(domain_score)
    if safe_browsing_result.matches:
        # A match is an independent threat-list confirmation, not a model guess.
        primary_scores.append(int(safe_browsing_result.risk_score))
    if image_path and vlm_result.available:
        primary_scores.append(int(vlm_result.risk_score))
    if image_path and image_model_result.available and image_model_score >= 70:
        # High-confidence phishing-layout matches are primary evidence. OCR can
        # legitimately miss tiny login text or a cropped browser address bar.
        primary_scores.append(image_model_score)

    secondary_scores = []
    if image_path:
        secondary_scores.append(int(visual_result.visual_score))
        if image_model_result.available:
            secondary_scores.append(image_model_score)

    max_primary = max(primary_scores)
    avg_primary = sum(primary_scores) / max(len(primary_scores), 1)

    if (
        image_path
        and vlm_result.available
        and vlm_result.verdict == "safe"
        and image_model_score < 65
        and int(text_result.risk_score) < 25
        and int(phishvn_result.risk_score) < 25
        and not safe_browsing_result.matches
    ):
        # Domain Gating confirmed benign / everyday photo:
        combined_score = min(int(max_primary * 0.35), 15)
    elif max_primary >= 60:
        corroborating = [s for s in primary_scores if s >= 40]
        if len(corroborating) >= 2:
            combined_score = int(0.75 * max_primary + 0.25 * (sum(corroborating) / len(corroborating)))
        else:
            combined_score = int(0.85 * max_primary + 0.15 * avg_primary)
    elif max_primary >= 25:
        combined_score = int(0.70 * max_primary + 0.30 * avg_primary)
    else:
        combined_score = int(avg_primary)

    # Corroborate with secondary signals (ELA/ResNet18)
    if secondary_scores and max(secondary_scores) >= 50 and combined_score >= 25:
        combined_score = min(100, combined_score + int(0.12 * max(secondary_scores)))

    # Structural URL evidence is deliberately conservative but must never be
    # averaged below the review threshold. Two independent medium image/text
    # signals can promote a fake authentication surface to high risk.
    if domain_score >= 20 and not trusted_domains_only:
        combined_score = max(combined_score, min(domain_score, 70))
    if (
        image_path
        and int(text_result.risk_score) >= 40
        and int(vlm_result.risk_score) >= 45
        and "biểu mẫu đăng nhập/xác thực" in text_result.highlighted_terms
    ):
        combined_score = max(combined_score, 60)
    if trusted_domains_only and int(text_result.risk_score) < 25 and not safe_browsing_result.matches:
        combined_score = min(combined_score, 15)

    combined_score = max(0, min(combined_score, 100))

    if combined_score >= 60:
        combined_level = "nguy_hiem"
    elif combined_score >= 25:
        combined_level = "nghi_ngo"
    else:
        combined_level = "an_toan"

    combined_scam_type = text_result.scam_type
    if safe_browsing_result.matches:
        combined_scam_type = "verified_unsafe_url"
    elif domain_score >= 50:
        combined_scam_type = "phishing_url"
    elif calibrated_phishvn_score >= 50 and calibrated_phishvn_score >= text_result.risk_score:
        combined_scam_type = "phishing_url"
    elif image_path and image_model_result.available and image_model_score >= 65 and combined_scam_type == "none":
        combined_scam_type = "phishing"

    suggested_action = text_result.suggested_action
    if safe_browsing_result.matches:
        suggested_action = (
            "Google Safe Browsing đã trả về kết quả khớp với danh sách URL nguy hiểm đã biết. "
            "Không mở URL, không đăng nhập và không cung cấp OTP hoặc thông tin thanh toán."
        )
    elif domain_score >= 50:
        suggested_action = (
            "Cấu trúc tên miền có dấu hiệu giả mạo mạnh. Không mở URL hoặc nhập thông tin; "
            "hãy tự gõ địa chỉ website chính thức để xác minh."
        )
    elif calibrated_phishvn_score >= 60:
        suggested_action = (
            "KHÔNG mở URL, KHÔNG đăng nhập hoặc cung cấp OTP/thông tin thanh toán. "
            "Hãy tự nhập địa chỉ website chính thức hoặc liên hệ tổ chức qua kênh đã xác minh."
        )
    elif phishvn_result.risk_score >= 25 and text_result.risk_score < 25:
        suggested_action = (
            "URL có dấu hiệu cần kiểm tra thêm. Không bấm trực tiếp; hãy đối chiếu tên miền "
            "với website chính thức trước khi tiếp tục."
        )
    elif image_path and image_model_result.available and image_model_score >= 65:
        suggested_action = (
            "Ảnh có bố cục tương đồng với các trang giả mạo. Không nhập mật khẩu, OTP hoặc "
            "thông tin thanh toán; hãy tự mở ứng dụng hay website chính thức để xác minh."
        )

    combined_explanation, analysis_breakdown = build_analysis_explanation(
        extracted_text=analysis_text,
        text_result=text_result,
        phishvn_result=phishvn_result,
        safe_browsing_result=safe_browsing_result,
        phishvn_display_score=calibrated_phishvn_score,
        domain_intelligence=domain_intelligence,
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
        "phishvn_url_risk_score": calibrated_phishvn_score,
        "phishvn_raw_score": raw_phishvn_score,
        "phishvn_calibrated_score": calibrated_phishvn_score,
        "phishvn_urls": phishvn_result.predictions_as_dicts(),
        "google_safe_browsing": safe_browsing_result.to_dict(),
        "domain_intelligence": domain_intelligence,
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
        "detector": {"app_version": APP_VERSION, "git_commit": GIT_COMMIT},
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


@app.post("/check-urls-batch")
def check_urls_batch(payload: BatchUrlRequest):
    unique_urls = list(dict.fromkeys(value.strip() for value in payload.urls if value.strip()))[:50]
    results = []
    for url in unique_urls:
        if not extract_url_candidates(url):
            results.append({"url": url, "status": "invalid", "risk_score": 0, "risk_level": "unknown"})
            continue
        analysis = _analyze_content_payload(url)
        results.append({"url": url, "status": "checked", "risk_score": analysis["risk_score"], "risk_level": analysis["risk_level"], "domain_intelligence": analysis["domain_intelligence"], "google_safe_browsing": analysis["google_safe_browsing"]})
    return {"total": len(results), "results": results}


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


@app.post("/scan-feedback", status_code=201)
def create_scan_feedback(payload: ScanFeedbackRequest, db: Session = Depends(get_db)):
    """Store explicit user validation without requiring an account."""
    feedback = ScanFeedback(
        scan_id=payload.scan_id,
        client_scan_id=payload.client_scan_id,
        verdict=payload.verdict,
        predicted_level=payload.predicted_level,
        risk_score=payload.risk_score,
        source_type=payload.source_type,
        original_filename=payload.original_filename,
        note=(payload.note or "").strip() or None,
        evidence_snapshot={
            "highlighted_terms": payload.highlighted_terms[:30],
            "urls": payload.urls[:20],
        },
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"id": feedback.id, "status": feedback.review_status}


@app.get("/scan-feedback")
def list_scan_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem phản hồi")
    rows = db.query(ScanFeedback).order_by(ScanFeedback.created_at.desc()).limit(500).all()
    return [
        {
            "id": row.id, "scan_id": row.scan_id, "client_scan_id": row.client_scan_id,
            "verdict": row.verdict, "predicted_level": row.predicted_level,
            "risk_score": row.risk_score, "source_type": row.source_type,
            "original_filename": row.original_filename, "note": row.note,
            "review_status": row.review_status, "created_at": row.created_at,
        }
        for row in rows
    ]


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
            extension = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}.get(image_format)
            if not extension:
                raise HTTPException(status_code=400, detail="Chỉ hỗ trợ ảnh JPEG, PNG hoặc WEBP")
            if width < 16 or height < 16 or width * height > 25_000_000:
                raise HTTPException(status_code=400, detail="Kích thước ảnh không hợp lệ hoặc vượt quá 25 megapixel")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="File không phải ảnh hợp lệ hoặc đã bị hỏng") from exc
        final_path = UPLOAD_DIR / f"{upload_id}{extension}"
        saved_path.replace(final_path)
        saved_path = final_path
        saved_name = final_path.name

        category_id = scam_category_id
        if category_id is None:
            category = db.query(ScamCategory).filter(ScamCategory.code == "phishing_screenshot").first()
            category_id = category.id if category else None

        # OCR and QR decoding both read the original image but are otherwise
        # independent, so neither needs to wait for the other to finish.
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="image-read") as executor:
            ocr_future = executor.submit(extract_text_and_boxes, saved_path)
            qr_future = executor.submit(decode_qr_codes, saved_path)
            extracted_text, ocr_words = ocr_future.result()
            qr_codes = qr_future.result()
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

        response = {
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
        completed_scan = True
        return response

    finally:
        if not completed_scan:
            Path(saved_path).unlink(missing_ok=True)


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


@app.post("/model-evaluations/run")
def run_model_evaluation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run the versioned regression suite against the same live scan pipeline."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được chạy đánh giá model")

    result = run_detector_benchmark(_analyze_content_payload)
    active_model = (
        db.query(AiModel)
        .filter(AiModel.is_active.is_(True))
        .order_by(AiModel.created_at.desc())
        .first()
    )
    saved_evaluation_id = None
    if active_model:
        evaluation = ModelEvaluation(
            ai_model_id=active_model.id,
            macro_f1=result["macro_f1"],
            recall=result["binary"]["recall"],
            false_alarm_rate=result["binary"]["false_alarm_rate"],
            explanation_usefulness=None,
        )
        db.add(evaluation)
        db.flush()
        saved_evaluation_id = evaluation.id
        db.add(SystemActivityLog(
            admin_id=current_user.id,
            action_type="automated_model_evaluation",
            description=(
                f"{result['suite']}: {result['passed']}/{result['total']} passed; "
                f"version={APP_VERSION}; commit={GIT_COMMIT}"
            ),
        ))
        db.commit()

    return {
        **result,
        "runtime": _runtime_info(),
        "active_model_id": active_model.id if active_model else None,
        "saved_evaluation_id": saved_evaluation_id,
    }


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
    return _runtime_info()


@app.get("/version")
def version_info():
    return _runtime_info()
