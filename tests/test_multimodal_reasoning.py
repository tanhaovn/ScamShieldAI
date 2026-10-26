"""Tests for the Multimodal Chain-of-Thought (CoT) Reasoning Engine & ResNet-18."""
from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.ai.reasoning_engine import execute_multimodal_reasoning
from backend.app.ai.vlm_image_analyzer import analyze_image_context


def test_resnet18_model_is_available_and_predicts():
    # Test inference on an existing dataset sample
    result = analyze_phishing_image("phishing_dataset/phishing/404/homepage.png")
    assert result.available is True
    assert 0.0 <= result.probability <= 1.0
    assert result.label in {"phishing", "legitimate"}
    assert "Model ảnh ước tính" in result.explanation


def test_multimodal_reasoning_detects_gov_impersonation():
    result = execute_multimodal_reasoning(
        ocr_text="LỆNH BẮT TẠM GIAM TỪ BỘ CÔNG AN. Yêu cầu chuyển tiền nộp phạt 50.000.000đ ngay lập tức trong 24h.",
        qr_codes=["https://fake-congan.vn/pay"],
        visual_flags=["Phát hiện dấu vết chỉnh sửa ELA (Error Level Analysis)"],
        image_model_probability=0.88,
        phishvn_url_score=85,
    )
    assert result.available is True
    assert result.verdict == "high_risk"
    assert result.risk_score >= 80
    assert any("Bộ Công An" in step or "hành pháp" in step for step in result.chain_of_thought)
    assert any("chuyển tiền" in ind.lower() or "dữ liệu nhạy cảm" in ind.lower() for ind in result.risk_indicators)


def test_multimodal_reasoning_detects_bank_otp_scam():
    result = execute_multimodal_reasoning(
        ocr_text="Vietcombank thông báo: Tài khoản của quý khách bị khóa. Vui lòng nhập mã OTP và mật khẩu để xác minh.",
        visual_flags=[],
        image_model_probability=0.75,
        phishvn_url_score=70,
    )
    assert result.available is True
    assert result.verdict == "high_risk"
    assert any("ngân hàng" in step.lower() and "otp" in step.lower() for step in result.chain_of_thought)


def test_multimodal_reasoning_on_safe_content():
    result = execute_multimodal_reasoning(
        ocr_text="Cửa hàng tạp hóa hoa hồng. Bán bánh mì, cà phê, nước giải khát. Mở cửa từ 6h đến 22h.",
        visual_flags=[],
        image_model_probability=0.12,
        phishvn_url_score=0,
    )
    assert result.available is True
    assert result.verdict == "safe"
    assert result.risk_score < 25


def test_analyze_image_context_integration():
    vlm_res = analyze_image_context(
        "phishing_dataset/phishing/404/homepage.png",
        ocr_text="Khẩn cấp: Tài khoản tạm khóa, xác thực mã OTP ngay",
        qr_codes=[],
        visual_flags=["ELA flag"],
        image_model_probability=0.85,
        phishvn_url_score=60,
    )
    assert vlm_res.available is True
    assert vlm_res.verdict in {"high_risk", "suspicious"}
    assert len(vlm_res.risk_indicators) > 0
    assert len(vlm_res.chain_of_thought) > 0
