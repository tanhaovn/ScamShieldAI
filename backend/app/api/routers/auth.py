from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.config import GOOGLE_CLIENT_ID
from backend.app.core.security import auth_response, hash_password, verify_password
from backend.app.db.database import get_db
from backend.app.db.models import AuthIdentity, User
from backend.app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
)


router = APIRouter(tags=["Authentication"])


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "auth_provider": (
            user.auth_identities[0].provider if user.auth_identities else "password"
        ),
    }


@router.post("/register", status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    full_name = " ".join(payload.full_name.strip().split())
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=422, detail="Email không hợp lệ")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email đã được sử dụng")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=full_name,
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return auth_response(user)


@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")
    return auth_response(user)


@router.post("/admin/login")
def login_admin(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Tài khoản này không có quyền quản trị")
    return auth_response(user)


@router.post("/auth/google")
def authenticate_with_google(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
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
    return auth_response(user)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.patch("/me")
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
    return serialize_user(current_user)
