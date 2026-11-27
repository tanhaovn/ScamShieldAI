"""Create local demo user accounts and representative scan histories.

This script is intentionally disabled in production. It is idempotent: running
it again does not duplicate users or seeded history rows.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import APP_ENV
from backend.app.core.security import hash_password
from backend.app.db.database import Base, SessionLocal, engine
from backend.app.db.models import ScanHistory, User


DEMO_PASSWORD = "Demo@12345"
DEMO_USERS = [
    ("demo.an@example.com", "Nguyễn Minh An"),
    ("demo.binh@example.com", "Trần Gia Bình"),
    ("demo.chi@example.com", "Lê Ngọc Chi"),
]

HISTORY_SAMPLES = [
    {
        "seed_key": "safe-message",
        "source_type": "text",
        "original_filename": "Tin nhắn thông thường",
        "extracted_text": "Hẹn bạn 8 giờ sáng mai tại thư viện.",
        "risk_score": 4,
        "risk_level": "an_toan",
        "explanation": "Không phát hiện yêu cầu chuyển tiền, OTP hoặc đường dẫn đáng ngờ.",
        "suggested_action": "Có thể tiếp tục trao đổi như bình thường.",
    },
    {
        "seed_key": "suspicious-url",
        "source_type": "url",
        "original_filename": "https://xac-minh-tai-khoan.example/login",
        "extracted_text": "https://xac-minh-tai-khoan.example/login",
        "risk_score": 48,
        "risk_level": "nghi_ngo",
        "explanation": "Tên miền và nội dung đăng nhập cần được kiểm tra thêm.",
        "suggested_action": "Không nhập mật khẩu; hãy tự mở website chính thức.",
    },
    {
        "seed_key": "dangerous-payment",
        "source_type": "pdf",
        "original_filename": "yeu-cau-chuyen-tien.pdf",
        "extracted_text": "Chuyển tiền khẩn cấp để mở khóa tài khoản và gửi mã OTP.",
        "risk_score": 92,
        "risk_level": "nguy_hiem",
        "explanation": "Phát hiện yêu cầu chuyển tiền khẩn cấp và cung cấp OTP.",
        "suggested_action": "Không chuyển tiền hoặc cung cấp OTP; liên hệ tổ chức qua kênh chính thức.",
    },
]


def main() -> None:
    if APP_ENV == "production":
        raise RuntimeError("Không được seed tài khoản demo trong production")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created_users = 0
    created_histories = 0
    try:
        for user_index, (email, full_name) in enumerate(DEMO_USERS):
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                user = User(
                    email=email,
                    password_hash=hash_password(DEMO_PASSWORD),
                    full_name=full_name,
                    role="user",
                    is_active=True,
                )
                db.add(user)
                db.flush()
                created_users += 1

            existing_keys = {
                details.get("seed_key")
                for row in db.query(ScanHistory).filter(ScanHistory.user_id == user.id).all()
                if isinstance((details := row.highlighted_regions), dict)
            }
            for sample_index, sample in enumerate(HISTORY_SAMPLES):
                if sample["seed_key"] in existing_keys:
                    continue
                db.add(
                    ScanHistory(
                        user_id=user.id,
                        image_url="",
                        original_filename=sample["original_filename"],
                        extracted_text=sample["extracted_text"],
                        scam_category_id=None,
                        risk_score=sample["risk_score"],
                        risk_level=sample["risk_level"],
                        explanation=sample["explanation"],
                        highlighted_regions={
                            "seed_key": sample["seed_key"],
                            "source_type": sample["source_type"],
                            "terms": [],
                            "visual_flags": [],
                            "phishvn_urls": [],
                            "qr_codes": [],
                        },
                        suggested_action=sample["suggested_action"],
                        created_at=(
                            datetime.now(timezone.utc).replace(tzinfo=None)
                            - timedelta(days=user_index, hours=sample_index * 3)
                        ),
                    )
                )
                created_histories += 1
        db.commit()
    finally:
        db.close()

    print(f"Created users: {created_users}")
    print(f"Created histories: {created_histories}")
    print(f"Demo password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
