from sqlalchemy.orm import Session

from backend.app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_SEED_ENABLED
from backend.app.core.security import hash_password
from backend.app.db.database import Base, SessionLocal, engine
from backend.app.db.models import ScamCategory, User


def seed_default_categories(db: Session) -> None:
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
            db.add(
                ScamCategory(
                    code=code,
                    display_name=display_name,
                    description=description,
                )
            )

    if ADMIN_SEED_ENABLED:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not admin:
            admin = db.query(User).filter(User.role == "admin").order_by(User.id.asc()).first()
        if admin:
            admin.email = ADMIN_EMAIL
            admin.password_hash = hash_password(ADMIN_PASSWORD)
            admin.full_name = "Quản trị viên"
            admin.role = "admin"
            admin.is_active = True
        else:
            db.add(
                User(
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    full_name="Quản trị viên",
                    role="admin",
                    is_active=True,
                )
            )

    db.commit()


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()
