"""
Risk Engine: phân tích văn bản trích từ ảnh (hoặc nhập trực tiếp) để tính risk score
và sinh giải thích. Bản này dùng rule-based (từ khóa + regex) để CHẠY ĐƯỢC NGAY
và tự giải thích rõ ràng — đây cũng là baseline hợp lý để so sánh khi sau này
thay bằng model ML (vd fine-tune PhoBERT) mà không đổi kiến trúc hệ thống.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict


# Từ điển từ khóa lừa đảo phổ biến tiếng Việt, nhóm theo loại + trọng số.
# Trong thực tế nên load từ bảng scam_keywords trong MySQL thay vì hardcode,
# để admin có thể cập nhật từ dashboard mà không cần deploy lại code.
SCAM_KEYWORDS: Dict[str, List[tuple]] = {
    "phishing": [
        ("chuyển khoản gấp", 15),
        ("tài khoản bị khóa", 15),
        ("xác minh ngay", 12),
        ("trúng thưởng", 15),
        ("mã otp", 20),
        ("cập nhật thông tin", 10),
        ("đăng nhập ngay", 10),
    ],
    "impersonation": [
        ("cơ quan công an", 20),
        ("nợ xấu", 15),
        ("cơ quan điều tra", 20),
        ("đại diện ngân hàng", 12),
    ],
    "fake_invoice": [
        ("phí vận chuyển", 10),
        ("shipper", 8),
        ("thanh toán đơn hàng", 8),
        ("hóa đơn chưa thanh toán", 12),
    ],
    "job_scam": [
        ("tuyển nhân viên", 15),
        ("lương hàng tháng", 12),
        ("làm việc tại nhà", 10),
        ("ít nhất 500k", 10),
        ("sau 15 phút", 10),
        ("nhận tiền", 10),
        ("phí dịch vụ", 12),
    ],
    "urgent_account_threat": [
        ("tài khoản của bạn", 10),
        ("bị trừ", 15),
        ("trong 2 giờ", 15),
        ("nhấn vào", 10),
        ("dịch vụ tài chính", 10),
    ],
}

# Regex phát hiện URL rút gọn / đáng ngờ
SUSPICIOUS_URL_PATTERN = re.compile(
    r"(bit\.ly|tinyurl|t\.me|zalo\.me(?:/|$)|shorturl|\.xyz|\.top|\.click|\.info)",
    re.IGNORECASE,
)

# Regex phát hiện số điện thoại / số tài khoản trần trong văn bản (dấu hiệu giục chuyển tiền)
BANK_ACCOUNT_PATTERN = re.compile(r"\b\d{9,16}\b")


@dataclass
class RiskResult:
    risk_score: int
    risk_level: str  # an_toan | nghi_ngo | nguy_hiem
    scam_type: str
    highlighted_terms: List[str] = field(default_factory=list)
    explanation: str = ""
    suggested_action: str = ""


def analyze_text(text: str) -> RiskResult:
    """
    Phân tích văn bản (đã OCR hoặc nhập tay) và trả về đánh giá rủi ro đầy đủ.
    """
    if not text or not text.strip():
        return RiskResult(
            risk_score=0,
            risk_level="an_toan",
            scam_type="none",
            explanation="Không trích được văn bản từ ảnh để phân tích.",
            suggested_action="Thử tải lại ảnh rõ nét hơn.",
        )

    text_lower = text.lower()
    normalized_text = _remove_diacritics(text_lower)
    score = 0
    matched_terms: List[str] = []
    category_scores: Dict[str, int] = {}

    for category, keywords in SCAM_KEYWORDS.items():
        for keyword, weight in keywords:
            if _remove_diacritics(keyword) in normalized_text:
                score += weight
                matched_terms.append(keyword)
                category_scores[category] = category_scores.get(category, 0) + weight

    url_matches = SUSPICIOUS_URL_PATTERN.findall(text_lower)
    if url_matches:
        score += 20
        matched_terms.extend(set(url_matches))
        category_scores["phishing"] = category_scores.get("phishing", 0) + 20

    if BANK_ACCOUNT_PATTERN.search(text) and any(
        _remove_diacritics(k) in normalized_text
        for k in ["chuyển khoản", "tài khoản", "otp"]
    ):
        score += 10
        matched_terms.append("số tài khoản/OTP kèm yêu cầu chuyển khoản")

    score = min(score, 100)

    if score >= 60:
        risk_level = "nguy_hiem"
    elif score >= 25:
        risk_level = "nghi_ngo"
    else:
        risk_level = "an_toan"

    scam_type = max(category_scores, key=category_scores.get) if category_scores else "none"

    explanation = _build_explanation(matched_terms, scam_type, risk_level)
    suggested_action = _build_suggested_action(risk_level, scam_type)

    return RiskResult(
        risk_score=score,
        risk_level=risk_level,
        scam_type=scam_type,
        highlighted_terms=sorted(set(matched_terms)),
        explanation=explanation,
        suggested_action=suggested_action,
    )


def _remove_diacritics(value: str) -> str:
    value = value.translate(str.maketrans({"đ": "d", "Đ": "D"}))
    return "".join(
        character
        for character in unicodedata.normalize("NFD", value)
        if unicodedata.category(character) != "Mn"
    )


def _build_explanation(matched_terms: List[str], scam_type: str, risk_level: str) -> str:
    if risk_level == "an_toan":
        return "Không phát hiện cụm từ hoặc dấu hiệu bất thường đáng kể trong nội dung."

    terms_str = ", ".join(f"'{t}'" for t in matched_terms[:5])
    scam_type_vn = {
        "phishing": "lừa đảo giả mạo (phishing)",
        "impersonation": "giả mạo cơ quan/tổ chức",
        "fake_invoice": "hóa đơn giả",
        "none": "chưa xác định rõ loại",
    }.get(scam_type, scam_type)

    return (
        f"Nội dung có dấu hiệu {scam_type_vn}. "
        f"Phát hiện các cụm từ/yếu tố đáng ngờ: {terms_str}. "
        f"Đây là các mẫu ngôn ngữ hoặc yếu tố thường xuất hiện trong nội dung lừa đảo."
    )


def _build_suggested_action(risk_level: str, scam_type: str) -> str:
    if risk_level == "an_toan":
        return "Nội dung có vẻ an toàn, vẫn nên thận trọng nếu liên quan đến giao dịch tiền."
    if risk_level == "nghi_ngo":
        return (
            "Xác minh lại thông tin qua kênh chính thức (tổng đài, website chính thức) "
            "trước khi thực hiện bất kỳ giao dịch hoặc cung cấp thông tin cá nhân nào."
        )
    return (
        "KHÔNG cung cấp thông tin cá nhân, KHÔNG chuyển khoản, KHÔNG nhấp vào liên kết. "
        "Xác minh trực tiếp với tổ chức liên quan qua số điện thoại chính thức, "
        "và cân nhắc báo cáo tới cơ quan chức năng hoặc tổng đài chống lừa đảo."
    )
