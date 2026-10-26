"""Tests for the upgraded Intelligent Dynamic Safety Assistant."""
from backend.app.risk.safety_assistant import answer_safety_question


def test_safety_assistant_handles_cccd_leak():
    ans = answer_safety_question(
        question="Tôi lỡ chụp ảnh CCCD gửi cho họ rồi thì có sao không?",
        risk_level="nguy_hiem",
        risk_score=90,
        highlighted_terms=["xác minh tài khoản", "gửi cccd"],
        urls=[],
        suggested_action="Dừng tương tác ngay lập tức",
        verdict="Nội dung lừa đảo mạo danh",
    )
    assert "CCCD" in ans
    assert "VNeID" in ans or "Công an" in ans or "CIC" in ans


def test_safety_assistant_handles_police_threat():
    ans = answer_safety_question(
        question="Công an gửi lệnh bắt đòi tôi nộp phạt thì phải làm sao?",
        risk_level="nguy_hiem",
        risk_score=95,
        highlighted_terms=["Bộ Công An", "lệnh bắt"],
        urls=[],
        suggested_action="Không nộp tiền",
        verdict="Mạo danh cơ quan bảo vệ pháp luật",
    )
    assert "TUYỆT ĐỐI KHÔNG" in ans or "yên tâm" in ans
    assert "Công an" in ans


def test_safety_assistant_handles_malicious_apk():
    ans = answer_safety_question(
        question="Họ gửi link bắt tôi cài app APK dịch vụ công thì sao?",
        risk_level="nguy_hiem",
        risk_score=85,
        highlighted_terms=["tải app dịch vụ công"],
        urls=[{"url": "dichvucong-fake.apk", "risk_score": 90}],
        suggested_action="Không cài file",
        verdict="Phát hiện mã độc",
    )
    assert "mã độc" in ans.lower() or "apk" in ans.lower()


def test_safety_assistant_explains_specific_reasons():
    ans = answer_safety_question(
        question="Tại sao bức ảnh này lại nguy hiểm ở đâu vậy?",
        risk_level="nguy_hiem",
        risk_score=92,
        highlighted_terms=["Vietcombank", "mã OTP"],
        urls=[{"url": "vcb-login.xyz", "risk_score": 88}],
        suggested_action="Không nhập OTP",
        verdict="Dấu hiệu chiếm quyền điều khiển tài khoản",
    )
    assert "Vietcombank" in ans or "mã OTP" in ans
    assert "vcb-login.xyz" in ans
