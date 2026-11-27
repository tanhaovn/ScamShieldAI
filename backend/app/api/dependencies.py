from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import decode_token
from backend.app.db.database import get_db
from backend.app.db.models import User


def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu token xác thực")

    token = authorization.replace("Bearer ", "", 1).strip()
    try:
        user_id = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token không hợp lệ") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return user


def get_optional_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User | None:
    """Return the signed-in user while allowing requests without a token."""
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token xác thực không hợp lệ")

    token = authorization.replace("Bearer ", "", 1).strip()
    try:
        user_id = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại hoặc đã bị khóa")
    return user
