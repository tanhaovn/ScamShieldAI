import json

from backend.app.ai import google_safe_browsing as gsb
from backend.app.main import _analyze_content_payload


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_safe_browsing_is_optional_without_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_SAFE_BROWSING_API_KEY", raising=False)
    result = gsb.check_urls(["https://example.com/login"])

    assert result.configured is False
    assert result.available is False
    assert result.risk_score == 0


def test_safe_browsing_returns_authoritative_threat_match(monkeypatch):
    monkeypatch.setenv("GOOGLE_SAFE_BROWSING_API_KEY", "test-key")
    gsb._result_cache.clear()
    monkeypatch.setattr(
        gsb.urllib.request,
        "urlopen",
        lambda request, timeout: _FakeResponse(
            {
                "threats": [
                    {
                        "url": "https://malicious.example/login",
                        "threatTypes": ["SOCIAL_ENGINEERING"],
                    }
                ],
                "cacheDuration": "600s",
            }
        ),
    )

    result = gsb.check_urls(["https://malicious.example/login"])

    assert result.available is True
    assert result.risk_score == 100
    assert result.matches[0].threat_labels == ["lừa đảo hoặc kỹ nghệ xã hội"]
    assert result.cache_duration_seconds == 600


def test_google_match_cannot_be_overridden_as_safe(monkeypatch):
    verified_match = gsb.SafeBrowsingResult(
        configured=True,
        available=True,
        checked_urls=["https://malicious.example/login"],
        matches=[
            gsb.SafeBrowsingMatch(
                url="https://malicious.example/login",
                threat_types=["SOCIAL_ENGINEERING"],
                threat_labels=["lừa đảo hoặc kỹ nghệ xã hội"],
            )
        ],
    )
    monkeypatch.setattr(
        "backend.app.main.check_google_safe_browsing",
        lambda urls: verified_match,
    )

    payload = _analyze_content_payload("https://malicious.example/login")

    assert payload["risk_level"] == "nguy_hiem"
    assert payload["risk_score"] >= 85
    assert payload["scam_type"] == "verified_unsafe_url"
    assert any(
        item["key"] == "google_safe_browsing"
        for item in payload["analysis_breakdown"]["components"]
    )
