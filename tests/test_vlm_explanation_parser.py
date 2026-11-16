from backend.app.ai.vlm_image_analyzer import _has_causal_explanation, _parse_response


def test_line_protocol_preserves_model_generated_evidence():
    result = _parse_response(
        "VERDICT: high_risk\n"
        "CONFIDENCE: 88%\n"
        "SUMMARY: Tin nhắn giả mạo ngân hàng để chiếm tài khoản.\n"
        "EVIDENCE_1: Đe dọa khóa tài khoản || giữa ảnh || tạo áp lực khiến nạn nhân bấm liên kết\n"
        "ACTION: Không bấm liên kết."
    )

    assert result["verdict"] == "high_risk"
    assert result["confidence"] == 0.88
    assert result["evidence"][0]["location"] == "giữa ảnh"
    assert "tạo áp lực" in result["evidence"][0]["why_risky"]


def test_transcription_is_not_accepted_as_causal_explanation():
    transcription = "Tài khoản của quý khách đã bị khóa. Vui lòng đăng nhập và nhập mã OTP."
    explanation = "Kẻ gian tạo áp lực để dụ nạn nhân nhập OTP và chiếm tài khoản."

    assert _has_causal_explanation(transcription) is False
    assert _has_causal_explanation(explanation) is True
