from pydantic import BaseModel, Field


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


class ScamKeywordRequest(BaseModel):
    keyword: str = Field(min_length=2, max_length=255)
    category: str = Field(min_length=2, max_length=100)
    weight: int = Field(ge=1, le=50)
