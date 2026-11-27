import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


# AI modules read several feature flags at import time, so environment values
# must be loaded before routers import the analysis service.
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIR = PROJECT_ROOT / "frontend-react"
UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

USE_DEEPFAKE_MODEL = os.getenv("USE_DEEPFAKE_MODEL", "false").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-me")
RENDER_RUNTIME = os.getenv("RENDER", "").strip().lower() == "true"
APP_ENV = os.getenv(
    "APP_ENV",
    "production" if RENDER_RUNTIME else "development",
).strip().lower()

if APP_ENV == "production" and JWT_SECRET == "dev-secret-key-change-me":
    raise RuntimeError("JWT_SECRET bắt buộc phải được cấu hình an toàn trong production")

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "" if APP_ENV == "production" else "admin@scamdetector.local",
).strip().lower()
ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "" if APP_ENV == "production" else "Admin@123",
)
if APP_ENV == "production" and (ADMIN_EMAIL or ADMIN_PASSWORD):
    if len(ADMIN_EMAIL) < 3:
        raise RuntimeError("ADMIN_EMAIL phải có ít nhất 3 ký tự khi bật tài khoản quản trị production")
    if len(ADMIN_PASSWORD) < 8 or ADMIN_PASSWORD == "Admin@123":
        raise RuntimeError("ADMIN_PASSWORD production phải có ít nhất 8 ký tự và không dùng mật khẩu mặc định")

ADMIN_SEED_ENABLED = bool(ADMIN_EMAIL and ADMIN_PASSWORD)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
APP_VERSION = os.getenv("APP_VERSION", "1.2.0").strip() or "1.2.0"
STARTED_AT = datetime.now(timezone.utc)

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173"
    if APP_ENV != "production"
    else ""
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]
