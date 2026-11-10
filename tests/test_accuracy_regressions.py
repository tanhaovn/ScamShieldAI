from backend.app.main import _analyze_content_payload


def test_official_microsoft_and_apple_domains_are_safe():
    for url in ("https://www.microsoft.com/", "https://www.apple.com/"):
        result = _analyze_content_payload(url)
        assert result["risk_level"] == "an_toan", (url, result["risk_score"])


def test_job_scam_with_upfront_payment_is_dangerous():
    result = _analyze_content_payload(
        "Tuyển cộng tác viên online lương cao. Nạp 500.000 đồng để làm nhiệm vụ và nhận hoa hồng ngay."
    )

    assert result["risk_level"] == "nguy_hiem"
    assert result["risk_score"] >= 60


def test_authority_requesting_transfer_is_dangerous():
    result = _analyze_content_payload(
        "Bộ Công an yêu cầu chuyển khoản gấp 20 triệu để phục vụ điều tra."
    )

    assert result["risk_level"] == "nguy_hiem"
    assert result["risk_score"] >= 60
