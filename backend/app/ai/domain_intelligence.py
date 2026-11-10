"""Offline domain intelligence; never connects to or opens submitted URLs."""
from __future__ import annotations

import ipaddress
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from urllib.parse import urlsplit


BRANDS = ("vietcombank", "vietinbank", "bidv", "agribank", "techcombank", "mbbank", "momo", "zalopay", "shopee", "tiktok", "facebook", "google", "microsoft", "apple", "netflix")
RISKY_TLDS = {"zip", "mov", "top", "click", "work", "support", "country", "gq", "tk", "ml", "cf", "xyz"}
SHORTENER_DOMAINS = {"bit.ly", "tinyurl.com", "t.co", "shorturl.at", "cutt.ly", "is.gd"}
MULTI_PART_SUFFIXES = {"com.vn", "net.vn", "org.vn", "gov.vn", "edu.vn", "co.uk", "org.uk", "com.au", "co.jp"}
# Small, auditable regression set. This only suppresses an isolated local-model
# prediction; Google Safe Browsing matches and risky path/content still win.
TRUSTED_DOMAINS = {"google.com", "microsoft.com", "apple.com", "vietcombank.com.vn"}


@dataclass
class DomainFinding:
    url: str
    host: str
    score: int
    level: str
    registered_domain: str = ""
    trusted: bool = False
    signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def _registered_domain(host: str) -> tuple[str, str, int]:
    labels = host.split(".")
    suffix_size = 2 if len(labels) >= 3 and ".".join(labels[-2:]) in MULTI_PART_SUFFIXES else 1
    if len(labels) <= suffix_size:
        return host, labels[0], 0
    name_index = len(labels) - suffix_size - 1
    return ".".join(labels[name_index:]), labels[name_index], name_index


def inspect_url(value: str) -> DomainFinding | None:
    candidate = value.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    try:
        parsed = urlsplit(candidate)
        host = (parsed.hostname or "").strip(".").lower()
    except ValueError:
        return None
    if not host:
        return None

    score = 0
    signals: list[str] = []
    is_ip = False
    try:
        ipaddress.ip_address(host)
        is_ip = True
        score += 35
        signals.append("URL dùng địa chỉ IP thay cho tên miền")
    except ValueError:
        pass
    if host.startswith("xn--") or ".xn--" in host:
        score += 32
        signals.append("Tên miền dùng Punycode, có thể chứa ký tự giả mạo")
    labels = host.split(".")
    registered_hint, name, subdomain_count = _registered_domain(host) if not is_ip else (host, host, 0)
    trusted = registered_hint in TRUSTED_DOMAINS
    tld = labels[-1]
    if subdomain_count > 2:
        score += min(20, (subdomain_count - 2) * 5)
        signals.append("Tên miền có nhiều lớp subdomain dễ gây nhầm lẫn")
    if registered_hint in SHORTENER_DOMAINS:
        score += 28
        signals.append("URL sử dụng dịch vụ rút gọn nên che khuất đích đến thật")
    if name.count("-") >= 2 or host.count("-") >= 3:
        score += 14
        signals.append("Tên miền sử dụng nhiều dấu gạch nối")
    if tld in RISKY_TLDS:
        score += 16
        signals.append(f"Phần mở rộng .{tld} thường cần được kiểm tra kỹ")
    if parsed.scheme != "https":
        score += 8
        signals.append("URL không sử dụng HTTPS")
    if "@" in parsed.netloc:
        score += 28
        signals.append("URL chứa ký tự @ có thể che giấu tên miền thật")
    if len(host) > 45:
        score += 10
        signals.append("Tên miền dài bất thường")
    if _entropy(name.replace("-", "")) > 3.75 and len(name) >= 12:
        score += 12
        signals.append("Tên miền có chuỗi ký tự ngẫu nhiên khó đọc")
    for brand in BRANDS:
        if brand in host and brand != name:
            score += 24
            signals.append(f"Tên thương hiệu “{brand}” xuất hiện ngoài tên miền chính")
            break
    if re.search(r"(?:login|verify|secure|account|otp|payment|wallet|update)", name) and any(brand in host for brand in BRANDS):
        score += 18
        signals.append("Kết hợp thương hiệu với từ khóa đăng nhập/xác minh")

    if trusted and not signals:
        score = 0
    score = min(score, 100)
    level = "high" if score >= 50 else "review" if score >= 20 else "low"
    return DomainFinding(value, host, score, level, registered_hint, trusted, signals)


def inspect_urls(urls: list[str]) -> list[dict]:
    findings = []
    seen = set()
    for value in urls[:50]:
        finding = inspect_url(value)
        if finding and finding.host not in seen:
            findings.append(finding.to_dict())
            seen.add(finding.host)
    return findings
