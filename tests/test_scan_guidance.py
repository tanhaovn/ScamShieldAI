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


