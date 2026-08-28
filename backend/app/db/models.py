"""
Model ORM ánh xạ tới các bảng trong schema.sql.
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, TIMESTAMP, Enum, func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum("user", "sme", "admin", name="user_role"), default="user")
    created_at = Column(TIMESTAMP, server_default=func.now())

    scans = relationship("ScanHistory", back_populates="user")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    input_type = Column(Enum("text", "image", "url", "audio", name="input_type"), nullable=False)
    original_filename = Column(String(512))
    extracted_text = Column(Text)
    risk_score = Column(Integer, nullable=False)
    text_risk_score = Column(Integer, default=0)
    visual_risk_score = Column(Integer, default=0)
    risk_level = Column(Enum("an_toan", "nghi_ngo", "nguy_hiem", name="risk_level"), nullable=False)
    scam_type = Column(String(100))
    explanation = Column(Text)
    highlighted_terms = Column(JSON)
    visual_flags = Column(JSON)
    suggested_action = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="scans")
