import math

import pytest

from backend.app.ai.phishvn_url_model import (
    BUNDLED_MODEL_PATH,
    analyze_urls_in_text,
    build_url_features,
    extract_url_candidates,
)


def test_extract_url_candidates_does_not_join_sentence_boundaries():
    text = "Đăng nhập tại tiktokshopseller-vn.com ngay. Hoặc https://google.com"
    assert extract_url_candidates(text) == [
        "tiktokshopseller-vn.com",
        "https://google.com",
    ]


def test_extract_url_candidates_supports_ip_urls():
    assert extract_url_candidates("Mở http://192.168.10.20/login để kiểm tra") == [
        "http://192.168.10.20/login"
    ]
    assert build_url_features("http://192.168.10.20/login")["is_ip"] == 1


def test_features_match_phishvn_reference_row():
    features = build_url_features("http://nhancode.online/ae2r8")
    assert features["url_len"] == 21
    assert features["dom_len"] == 15
    assert features["letter_cnt"] == 17
    assert features["digit_cnt"] == 2
    assert features["special_cnt"] == 2
    assert features["slash_cnt"] == 1
    assert features["path_len"] == 5
    assert math.isclose(features["entropy"], 3.594465636961452)


def test_bundled_phishvn_model_detects_known_test_url():
    pytest.importorskip("sklearn")
    if not BUNDLED_MODEL_PATH.exists():
        pytest.skip("PhishVN results bundle is not present")

    result = analyze_urls_in_text("Truy cập tiktokshopseller-vn.com để xác minh")
    assert result.available is True
    assert result.predictions
    assert result.predictions[0].label == "phishing"
    assert result.predictions[0].probability > 0.8
