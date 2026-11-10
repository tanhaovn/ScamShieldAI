import pytest
from pydantic import ValidationError

from backend.app.main import BatchUrlRequest, ScanFeedbackRequest, ScamKeywordRequest


def test_feedback_contract_accepts_three_supported_verdicts():
    for verdict in ("correct", "false_alarm", "missed_scam"):
        payload = ScanFeedbackRequest(
            verdict=verdict,
            predicted_level="nghi_ngo",
            risk_score=45,
            source_type="url",
        )
        assert payload.verdict == verdict


def test_feedback_contract_rejects_unknown_verdict_and_score():
    with pytest.raises(ValidationError):
        ScanFeedbackRequest(
            verdict="maybe",
            predicted_level="nghi_ngo",
            risk_score=120,
            source_type="url",
        )


def test_batch_contract_limits_request_to_50_urls():
    assert len(BatchUrlRequest(urls=["https://example.com"]).urls) == 1
    with pytest.raises(ValidationError):
        BatchUrlRequest(urls=[f"https://example.com/{index}" for index in range(51)])


def test_dynamic_keyword_contract_limits_weight():
    assert ScamKeywordRequest(keyword="xác minh gấp", category="phishing", weight=20).weight == 20
    with pytest.raises(ValidationError):
        ScamKeywordRequest(keyword="xác minh gấp", category="phishing", weight=99)
