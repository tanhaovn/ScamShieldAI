"""Tests for Domain Gating and Calibrated Fusion (False Positive Prevention)."""
import tempfile
from pathlib import Path
from PIL import Image

from backend.app.ai.reasoning_engine import execute_multimodal_reasoning
from backend.app.main import _analyze_content_payload


def test_everyday_photo_is_strictly_safe():
    # Simulate an everyday photo with ordinary or no text, no QR, no URL
    result = execute_multimodal_reasoning(
        ocr_text="Hôm nay trời đẹp quá, đi uống cà phê với bạn bè.",
        qr_codes=[],
        visual_flags=["Ảnh không có metadata EXIF"],
        image_model_probability=0.62,  # Even if ResNet has noisy prediction
        phishvn_url_score=0,
    )
    assert result.available is True
    assert result.verdict == "safe"
    assert result.risk_score == 0
    assert "Domain Gating" in result.chain_of_thought[0]


def test_strong_image_model_signal_is_not_gated_as_safe():
    result = execute_multimodal_reasoning(
        ocr_text="",
        qr_codes=[],
        visual_flags=[],
        image_model_probability=0.78,
        phishvn_url_score=0,
    )
    assert result.verdict in {"suspicious", "high_risk"}
    assert result.risk_score >= 25
    assert any("ResNet-18" in step for step in result.chain_of_thought)


def test_authentication_surface_requires_review():
    result = execute_multimodal_reasoning(
        ocr_text=(
            "Adobe Express Continue with Google Continue with Facebook "
            "Continue with Apple Continue with email"
        ),
        qr_codes=[],
        visual_flags=[],
        image_model_probability=0.32,
        phishvn_url_score=0,
    )
    assert result.verdict == "suspicious"
    assert result.risk_score >= 25


def test_random_image_without_text_is_safe(tmp_path):
    # Create a blank/noise test image
    image_path = tmp_path / "nature.jpg"
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    img.save(image_path)

    payload = _analyze_content_payload(
        "",  # No text extracted
        image_path=str(image_path),
        qr_codes=[],
    )
    assert payload["risk_level"] == "an_toan"
    assert payload["risk_score"] <= 20
    assert payload["vlm_analysis"]["verdict"] == "safe"


def test_scam_impersonation_still_triggers_high_risk(tmp_path):
    # Ensure real scams are still strongly caught
    image_path = tmp_path / "scam_bill.jpg"
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(image_path)

    payload = _analyze_content_payload(
        "LỆNH BẮT CỦA BỘ CÔNG AN: Chuyển tiền nộp phạt 50 triệu gấp vào STK 123456",
        image_path=str(image_path),
        qr_codes=[],
    )
    assert payload["risk_level"] == "nguy_hiem"
    assert payload["risk_score"] >= 60
    assert payload["vlm_analysis"]["verdict"] == "high_risk"
