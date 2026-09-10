"""
Kết nối database bằng SQLAlchemy.
Mặc định dùng SQLite cho local test/dev để app vẫn chạy khi MySQL chưa sẵn sàng.
Nếu muốn dùng MySQL thật, set USE_SQLITE=false và điền biến DB_* trong .env.
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() in {"1", "true", "yes", "y"}

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "scam_detector")

if USE_SQLITE:
    DATABASE_URL = "sqlite:///./scam_detector.db"
else:
    DATABASE_URL = (
        f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency dùng trong FastAPI để lấy session DB cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
