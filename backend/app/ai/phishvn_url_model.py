"""PhishVN URL-phishing inference for URLs extracted from OCR text.

PhishVN v3.1.0 is a URL dataset, not a labelled Vietnamese message corpus.
This module therefore extracts URL/domain candidates from OCR output and feeds
their 21 lexical features to the supplied HistGradientBoosting model. General
Vietnamese sentence analysis remains the responsibility of ``risk_engine``.
"""
from __future__ import annotations

import ipaddress
import math
import os
import re
import warnings
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(min(os.cpu_count() or 1, 8)))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHISHVN_ROOT = PROJECT_ROOT / "PhishVN A Time-Stamped Vietnamese URL Phishing Dat"
LOCAL_MODEL_PATH = PROJECT_ROOT / "models" / "phishvn_url_histgb.joblib"
BUNDLED_MODEL_PATH = PHISHVN_ROOT / "p1a_results_bundle" / "models" / "HistGB_seed0.joblib"

FEATURE_NAMES = [
    "url_len",
    "dom_len",
    "is_ip",
    "tld_len",
    "subdom_cnt",
    "letter_cnt",
    "digit_cnt",
    "special_cnt",
    "eq_cnt",
    "qm_cnt",
    "amp_cnt",
    "dot_cnt",
    "dash_cnt",
    "under_cnt",
    "letter_ratio",
    "digit_ratio",
    "spec_ratio",
    "slash_cnt",
    "entropy",
    "path_len",
    "query_len",
]

# Covers full URLs, www-prefixed URLs and bare domains commonly seen in OCR.
URL_PATTERN = re.compile(
    r"(?i)(?<![@\w])(?:https?://|www\.)?"
    r"(?:(?:[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?\.)+[a-z]{2,63}"
    r"|(?:\d{1,3}\.){3}\d{1,3})"
    r"(?::\d{2,5})?(?:/[^\s<>\"']*)?"
)
TRAILING_OCR_PUNCTUATION = ".,;:!?)]}>\"'"
COMMON_TLDS = (
    "com|net|org|vn|com\\.vn|gov\\.vn|edu\\.vn|io|co|info|biz|xyz|top|online|"
    "site|shop|live|vip|app|link|me|cc|tv|dev|cloud|tech|store|fun|club|pro|asia|mobi"
)

SUSPICIOUS_TLDS = {
    "app",
    "click",
    "info",
    "live",
    "online",
    "shop",
    "site",
    "top",
    "vip",
    "xyz",
}
LURE_TOKENS = {
    "chinhphu",
    "congan",
    "dangnhap",
    "dichvucong",
    "hoantien",
    "khuyenmai",
    "nhantien",
    "otp",
    "thanhtoan",
    "thue",
    "vandon",
    "xacminh",
}
BRAND_DOMAIN_HINTS = {
    "agribank": "agribank.com.vn",
    "bidv": "bidv.com.vn",
    "dichvucong": "dichvucong.gov.vn",
    "facebook": "facebook.com",
    "lazada": "lazada.vn",
    "mbbank": "mbbank.com.vn",
    "momo": "momo.vn",
    "shopee": "shopee.vn",
    "tiktok": "tiktok.com",
    "vietcombank": "vietcombank.com.vn",
    "vietinbank": "vietinbank.vn",
    "vtp": "viettelpost.com.vn",
    "zalopay": "zalopay.vn",
}

# The published 0.5 benchmark threshold favours recall (precision ~0.42 on the
# gold/silver temporal test). The user-facing app uses conservative bands to
# avoid presenting every uncertain URL as a definite phishing verdict.
SUSPICIOUS_THRESHOLD = 0.60
PHISHING_THRESHOLD = 0.80

_model_cache: Any = None
_model_path_cache: Path | None = None
_load_attempted = False


@dataclass
class UrlPrediction:
    url: str
    normalized_url: str
    domain: str
    probability: float
    label: str
    risk_score: int
    suspicious_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PhishVNTextResult:
    available: bool
    model_name: str
    risk_score: int
    predictions: list[UrlPrediction] = field(default_factory=list)
    explanation: str = ""

    def predictions_as_dicts(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.predictions]


def _configured_model_paths() -> list[Path]:
    configured = os.getenv("PHISHVN_MODEL_PATH", "").strip()
    paths = [Path(configured)] if configured else []
    paths.extend([LOCAL_MODEL_PATH, BUNDLED_MODEL_PATH])
    return paths


def _load_model() -> tuple[Any, Path | None]:
    """Lazy-load a trusted local model; gracefully disable if dependencies are absent."""
    global _model_cache, _model_path_cache, _load_attempted
    if _load_attempted:
        return _model_cache, _model_path_cache

    _load_attempted = True
    model_path = next((path for path in _configured_model_paths() if path.is_file()), None)
    if model_path is None:
        return None, None

    try:
        import joblib

        model = joblib.load(model_path)
        if not hasattr(model, "predict_proba"):
            return None, None
        expected = list(getattr(model, "feature_names_in_", FEATURE_NAMES))
        if expected != FEATURE_NAMES:
            return None, None
        _model_cache = model
        _model_path_cache = model_path
        return model, model_path
    except (ImportError, ModuleNotFoundError, OSError, ValueError, AttributeError):
        return None, None


def extract_url_candidates(text: str) -> list[str]:
    """Extract unique URL/domain candidates while preserving their OCR order."""
    if not text:
        return []

    # OCR sometimes inserts spaces around a domain dot. Limit compaction to
    # known TLDs so sentence endings such as "ngay. Hoặc" do not become URLs.
    compact = re.sub(
        rf"(?i)\b([a-z0-9][a-z0-9-]{{1,62}})\s*\.\s*({COMMON_TLDS})\b",
        r"\1.\2",
        text,
    )
    candidates: list[str] = []
    seen: set[str] = set()
    for match in URL_PATTERN.finditer(compact):
        candidate = match.group(0).rstrip(TRAILING_OCR_PUNCTUATION)
        key = candidate.lower()
        if candidate and key not in seen:
            candidates.append(candidate)
            seen.add(key)
    return candidates


def normalize_url(value: str) -> tuple[str, str, str, str]:
    """Return (scheme-stripped URL, domain, path, query) in PhishVN form."""
    candidate = value.strip().rstrip(TRAILING_OCR_PUNCTUATION)
    parsed = urlsplit(candidate if "://" in candidate else f"http://{candidate}")
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass

    try:
        port = f":{parsed.port}" if parsed.port else ""
    except ValueError:
        port = ""
    path = parsed.path or ""
    query = parsed.query or ""
    normalized = f"{host}{port}{path}"
    if query:
        normalized += f"?{query}"
    normalized = normalized.rstrip("/")
    return normalized, host, path.strip("/"), query


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in Counter(value).values())


def build_url_features(value: str) -> dict[str, float]:
    """Reproduce the 21-feature CompPhish schema shipped with PhishVN."""
    normalized, domain, path, query = normalize_url(value)
    length = max(len(normalized), 1)
    letters = sum(character.isalpha() for character in normalized)
    digits = sum(character.isdigit() for character in normalized)
    specials = sum(not character.isalnum() for character in normalized)
    labels = [part for part in domain.split(".") if part]
    tld = labels[-1] if labels else ""
    try:
        is_ip = int(bool(domain) and ipaddress.ip_address(domain) is not None)
    except ValueError:
        is_ip = 0

    return {
        "url_len": float(len(normalized)),
        "dom_len": float(len(domain)),
        "is_ip": float(is_ip),
        "tld_len": float(len(tld)),
        "subdom_cnt": float(max(len(labels) - 2, 0) if not is_ip else 0),
        "letter_cnt": float(letters),
        "digit_cnt": float(digits),
        "special_cnt": float(specials),
        "eq_cnt": float(normalized.count("=")),
        "qm_cnt": float(normalized.count("?")),
        "amp_cnt": float(normalized.count("&")),
        "dot_cnt": float(normalized.count(".")),
        "dash_cnt": float(normalized.count("-")),
        "under_cnt": float(normalized.count("_")),
        "letter_ratio": letters / length,
        "digit_ratio": digits / length,
        "spec_ratio": specials / length,
        "slash_cnt": float(normalized.count("/")),
        "entropy": _entropy(normalized),
        "path_len": float(len(path)),
        "query_len": float(len(query)),
    }


def explain_url_features(value: str, features: dict[str, float]) -> list[str]:
    """Produce human-readable lexical evidence without claiming model causality."""
    normalized, domain, _path, _query = normalize_url(value)
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    signals: list[str] = []
    if features["is_ip"]:
        signals.append("dùng địa chỉ IP thay cho tên miền")
    if "@" in normalized:
        signals.append("chứa ký tự @ có thể che giấu đích thật")
    if tld in SUSPICIOUS_TLDS:
        signals.append(f"đuôi .{tld} thường cần kiểm tra kỹ")
    if features["subdom_cnt"] >= 3:
        signals.append("có quá nhiều tầng tên miền phụ")
    if features["url_len"] >= 60:
        signals.append("URL dài bất thường")
    if features["digit_ratio"] >= 0.25:
        signals.append("tỷ lệ chữ số cao")
    if features["dash_cnt"] >= 3:
        signals.append("chứa nhiều dấu gạch nối")
    if domain.startswith("xn--") or ".xn--" in domain:
        signals.append("dùng tên miền quốc tế hóa/punycode")

    for brand, official_domain in BRAND_DOMAIN_HINTS.items():
        belongs_to_official_domain = domain == official_domain or domain.endswith(f".{official_domain}")
        if brand in domain and not belongs_to_official_domain:
            signals.append(
                f"có chuỗi '{brand}' gợi tên thương hiệu nhưng domain không thuộc {official_domain}"
            )
            break

    matched_tokens = sorted(token for token in LURE_TOKENS if token in normalized.lower())
    if matched_tokens:
        signals.append("chứa từ khóa nhử: " + ", ".join(matched_tokens[:4]))
    if not signals:
        signals.append(
            "cấu trúc quan sát được: "
            f"{int(features['url_len'])} ký tự, {int(features['dot_cnt'])} dấu chấm, "
            f"{int(features['dash_cnt'])} dấu gạch nối, entropy {features['entropy']:.2f}"
        )
        signals.append("tổ hợp đặc trưng trên giống nhóm URL abuse trong dữ liệu PhishVN")
    return signals


def analyze_urls_in_text(text: str) -> PhishVNTextResult:
    candidates = extract_url_candidates(text)
    if not candidates:
        return PhishVNTextResult(
            available=False,
            model_name="PhishVN-HistGB",
            risk_score=0,
            explanation="OCR không tìm thấy URL hoặc tên miền để PhishVN phân tích.",
        )

    model, model_path = _load_model()
    if model is None:
        return PhishVNTextResult(
            available=False,
            model_name="PhishVN-HistGB",
            risk_score=0,
            explanation=(
                "Đã tìm thấy URL nhưng chưa nạp được model PhishVN. "
                "Hãy cài scikit-learn và joblib theo requirements.txt."
            ),
        )

    predictions: list[UrlPrediction] = []
    phishing_class_index = list(model.classes_).index(1)
    for candidate in candidates:
        features = build_url_features(candidate)
        matrix = np.asarray([[features[name] for name in FEATURE_NAMES]], dtype=np.float64)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="X does not have valid feature names",
                category=UserWarning,
            )
            warnings.filterwarnings(
                "ignore",
                message="Could not find the number of physical cores.*",
                category=UserWarning,
            )
            probability = float(model.predict_proba(matrix)[0][phishing_class_index])
        normalized, domain, _path, _query = normalize_url(candidate)
        if probability >= PHISHING_THRESHOLD:
            label = "phishing"
            risk_score = round(probability * 100)
        elif probability >= SUSPICIOUS_THRESHOLD:
            label = "suspicious"
            risk_score = round(25 + ((probability - SUSPICIOUS_THRESHOLD) / 0.20) * 34)
        else:
            label = "benign"
            risk_score = round((probability / SUSPICIOUS_THRESHOLD) * 24)

        predictions.append(
            UrlPrediction(
                url=candidate,
                normalized_url=normalized,
                domain=domain,
                probability=round(probability, 4),
                label=label,
                risk_score=risk_score,
                suspicious_signals=explain_url_features(candidate, features),
            )
        )

    predictions.sort(key=lambda item: item.probability, reverse=True)
    highest = predictions[0]
    model_name = f"PhishVN-HistGB ({model_path.name})" if model_path else "PhishVN-HistGB"
    if highest.label == "phishing":
        explanation = (
            f"PhishVN cảnh báo '{highest.url}' với điểm mô hình {highest.probability * 100:.1f}%. "
            f"Dấu hiệu quan sát được: "
            + "; ".join(highest.suspicious_signals)
            + "."
        )
    elif highest.label == "suspicious":
        explanation = (
            f"PhishVN đánh giá '{highest.url}' ở mức cần kiểm tra thêm "
            f"(điểm mô hình {highest.probability * 100:.1f}%). Dấu hiệu quan sát được: "
            + "; ".join(highest.suspicious_signals)
            + "."
        )
    else:
        explanation = (
            f"PhishVN đã kiểm tra {len(predictions)} URL/domain; mức nghi ngờ cao nhất là "
            f"{highest.probability * 100:.1f}% tại '{highest.url}'."
        )

    return PhishVNTextResult(
        available=True,
        model_name=model_name,
        risk_score=highest.risk_score,
        predictions=predictions,
        explanation=explanation,
    )
