"""Optional Google Safe Browsing v5 reputation lookup for extracted URLs.

Google Safe Browsing is an independent, authoritative threat-list signal. It
must not be used to claim that an unlisted URL is safe, and Google attribution
must only accompany matches returned by this service.
"""
from __future__ import annotations

import ipaddress
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any


API_ENDPOINT = "https://safebrowsing.googleapis.com/v5/urls:search"
SOURCE_NAME = "Google Safe Browsing v5"
SOURCE_DOCUMENTATION = "https://developers.google.com/safe-browsing/"
MAX_URLS_PER_REQUEST = 50
MAX_UNSAFE_CACHE_SECONDS = 30 * 60
DEFAULT_CACHE_SECONDS = 5 * 60

THREAT_LABELS = {
    "SOCIAL_ENGINEERING": "lừa đảo hoặc kỹ nghệ xã hội",
    "MALWARE": "phát tán mã độc",
    "UNWANTED_SOFTWARE": "phần mềm không mong muốn",
    "POTENTIALLY_HARMFUL_APPLICATION": "ứng dụng có khả năng gây hại",
}


@dataclass
class SafeBrowsingMatch:
    url: str
    threat_types: list[str] = field(default_factory=list)
    threat_labels: list[str] = field(default_factory=list)


@dataclass
class SafeBrowsingResult:
    configured: bool
    available: bool
    checked_urls: list[str] = field(default_factory=list)
    matches: list[SafeBrowsingMatch] = field(default_factory=list)
    cache_duration_seconds: int = 0
    error: str = ""
    source: str = SOURCE_NAME
    source_documentation: str = SOURCE_DOCUMENTATION

    @property
    def risk_score(self) -> int:
        return 100 if self.matches else 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_score"] = self.risk_score
        payload["attribution"] = "Nguồn đối chiếu: Google Safe Browsing."
        payload["limitation"] = (
            "Không có kết quả khớp không đồng nghĩa URL chắc chắn an toàn; "
            "các mối đe dọa mới có thể chưa xuất hiện trong danh sách."
        )
        return payload


_result_cache: dict[tuple[str, ...], tuple[float, SafeBrowsingResult]] = {}


def _api_key() -> str:
    return os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()


def _normalise_public_url(value: str) -> str | None:
    candidate = value.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    try:
        parsed = urllib.parse.urlsplit(candidate)
        host = (parsed.hostname or "").strip().lower()
        if parsed.scheme not in {"http", "https"} or not host:
            return None
        try:
            address = ipaddress.ip_address(host)
            if address.is_private or address.is_loopback or address.is_link_local:
                return None
        except ValueError:
            if host == "localhost" or host.endswith(".local"):
                return None
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))
    except (TypeError, ValueError):
        return None


def _duration_seconds(value: str | None) -> int:
    if not value or not value.endswith("s"):
        return DEFAULT_CACHE_SECONDS
    try:
        return max(1, int(float(value[:-1])))
    except ValueError:
        return DEFAULT_CACHE_SECONDS


def check_urls(urls: list[str]) -> SafeBrowsingResult:
    """Check up to 50 public HTTP(S) URLs without ever opening those URLs."""
    key = _api_key()
    candidates = []
    seen: set[str] = set()
    for value in urls:
        normalised = _normalise_public_url(value)
        if normalised and normalised not in seen:
            candidates.append(normalised)
            seen.add(normalised)
        if len(candidates) >= MAX_URLS_PER_REQUEST:
            break

    if not key:
        return SafeBrowsingResult(configured=False, available=False, checked_urls=candidates)
    if not candidates:
        return SafeBrowsingResult(configured=True, available=True)

    cache_key = tuple(candidates)
    cached = _result_cache.get(cache_key)
    now = time.monotonic()
    if cached and cached[0] > now:
        return cached[1]

    query = urllib.parse.urlencode(
        [("key", key), ("alt", "json"), *(("urls", url) for url in candidates)]
    )
    request = urllib.request.Request(
        f"{API_ENDPOINT}?{query}",
        headers={"Accept": "application/json", "User-Agent": "SFDS-Scam-Detector/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        matches = []
        for item in data.get("threats", []):
            threat_types = [str(value) for value in item.get("threatTypes", [])]
            matches.append(
                SafeBrowsingMatch(
                    url=str(item.get("url") or ""),
                    threat_types=threat_types,
                    threat_labels=[THREAT_LABELS.get(value, value.lower()) for value in threat_types],
                )
            )
        cache_seconds = min(_duration_seconds(data.get("cacheDuration")), MAX_UNSAFE_CACHE_SECONDS)
        result = SafeBrowsingResult(
            configured=True,
            available=True,
            checked_urls=candidates,
            matches=matches,
            cache_duration_seconds=cache_seconds,
        )
        _result_cache[cache_key] = (now + cache_seconds, result)
        return result
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return SafeBrowsingResult(
            configured=True,
            available=False,
            checked_urls=candidates,
            error="Không thể kết nối Google Safe Browsing trong lần kiểm tra này.",
        )
