from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ocr.highlight_service import build_suspicious_regions


client = TestClient(app)


def _word(text, left, width, word_num):
    return {
        "text": text,
        "left": left,
        "top": 20,
        "width": width,
        "height": 18,
        "conf": 92.0,
        "block_num": 1,
        "par_num": 1,
        "line_num": 1,
        "word_num": word_num,
    }


def test_suspicious_regions_use_tight_ocr_coordinates():
    words = [
        _word("Tài", 10, 25, 1),
        _word("khoản", 42, 45, 2),
        _word("xác", 100, 26, 3),
        _word("minh", 132, 35, 4),
        _word("ngay", 173, 32, 5),
    ]

    regions = build_suspicious_regions(words, ["xác minh ngay"], [])

    assert len(regions) == 1
    assert regions[0]["left"] == 100
    assert regions[0]["width"] == 105
    assert regions[0]["severity"] == "warning"
    assert regions[0]["reason"]


def test_analysis_assistant_explains_only_scan_evidence():
    response = client.post(
        "/analysis-assistant",
        json={
            "question": "Vì sao bị cảnh báo?",
            "risk_level": "nguy_hiem",
            "risk_score": 88,
            "highlighted_terms": ["xác minh ngay", "OTP"],
            "urls": [{"url": "https://fake-bank.example", "risk_score": 91}],
            "suggested_action": "Không mở URL và không cung cấp OTP.",
            "verdict": "Nội dung có nhiều dấu hiệu giả mạo.",
        },
    )

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "xác minh ngay" in answer
    assert "fake-bank.example" in answer
    assert "Nội dung có nhiều dấu hiệu giả mạo" in answer


def test_analysis_assistant_gives_emergency_steps_after_click():
    response = client.post(
        "/analysis-assistant",
        json={
            "question": "Tôi đã bấm link thì làm gì?",
            "risk_level": "nguy_hiem",
            "risk_score": 90,
        },
    )

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert "đóng trang" in answer
    assert "đổi mật khẩu" in answer
