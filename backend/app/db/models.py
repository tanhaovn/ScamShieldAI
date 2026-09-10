"""
Model ORM ánh xạ tới các bảng trong schema.sql.
"""
from sqlalchemy import Boolean, Column, DECIMAL, Integer, String, Text, JSON, ForeignKey, TIMESTAMP, Enum, func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum("user", "admin", name="user_role"), default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    scans = relationship("ScanHistory", back_populates="user")
    training_dataset = relationship("TrainingDataset", back_populates="uploader")
    logs = relationship("SystemActivityLog", back_populates="admin")


class ScamCategory(Base):
    __tablename__ = "scam_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(150), nullable=False)
    description = Column(Text)

    scans = relationship("ScanHistory", back_populates="category")
    datasets = relationship("TrainingDataset", back_populates="category")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(1024), nullable=False)
    original_filename = Column(String(512))
    extracted_text = Column(Text)
    scam_category_id = Column(Integer, ForeignKey("scam_categories.id", ondelete="SET NULL"))
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(Enum("an_toan", "nghi_ngo", "nguy_hiem", name="risk_level"), nullable=False)
    explanation = Column(Text)
    highlighted_regions = Column(JSON)
    suggested_action = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="scans")
    category = relationship("ScamCategory", back_populates="scans")


class TrainingDataset(Base):
    __tablename__ = "training_dataset"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(1024), nullable=False)
    scam_category_id = Column(Integer, ForeignKey("scam_categories.id", ondelete="SET NULL"))
    is_anonymized = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("ScamCategory", back_populates="datasets")
    uploader = relationship("User", back_populates="training_dataset")


class AiModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    evaluations = relationship("ModelEvaluation", back_populates="model")


class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False)
    macro_f1 = Column(DECIMAL(5, 4))
    recall = Column(DECIMAL(5, 4))
    false_alarm_rate = Column(DECIMAL(5, 4))
    explanation_usefulness = Column(DECIMAL(5, 4))
    evaluated_at = Column(TIMESTAMP, server_default=func.now())

    model = relationship("AiModel", back_populates="evaluations")


class SystemActivityLog(Base):
    __tablename__ = "system_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action_type = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    admin = relationship("User", back_populates="logs")
