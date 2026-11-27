from pydantic import BaseModel, Field


class ScanImageRequest(BaseModel):
    scam_category_id: int | None = None
    risk_score: int | None = None


class TextCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


class UrlCheckRequest(BaseModel):
    url: str = Field(min_length=3, max_length=4096)


class BatchUrlRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=50)


class ExplanationEvidence(BaseModel):
    observation: str = Field(default="", max_length=1000)
    why_risky: str = Field(default="", max_length=2000)


class ExplanationFollowupRequest(BaseModel):
    question: str = Field(min_length=2, max_length=600)
    language: str = Field(default="vi", pattern="^(vi|en)$")
    risk_score: int = Field(default=0, ge=0, le=100)
    risk_level: str = Field(default="unknown", max_length=30)
    source_type: str = Field(default="unknown", max_length=30)
    explanation: str = Field(default="", max_length=8000)
    extracted_text: str = Field(default="", max_length=6000)
    evidence: list[ExplanationEvidence] = Field(default_factory=list, max_length=8)


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
