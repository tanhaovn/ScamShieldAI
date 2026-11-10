"""
Risk Engine: phân tích văn bản trích từ ảnh (hoặc nhập trực tiếp) để tính risk score
và sinh giải thích. Bản này dùng rule-based (từ khóa + regex) để CHẠY ĐƯỢC NGAY
và tự giải thích rõ ràng — đây cũng là baseline hợp lý để so sánh khi sau này
thay bằng model ML (vd fine-tune PhoBERT) mà không đổi kiến trúc hệ thống.
"""
import re
import unicodedata
import time
from dataclasses import dataclass, field
from typing import List, Dict


# Từ điển từ khóa lừa đảo phổ biến tiếng Việt, nhóm theo loại + trọng số.
# Trong thực tế nên load từ bảng scam_keywords trong MySQL thay vì hardcode,
# để admin có thể cập nhật từ dashboard mà không cần deploy lại code.
SCAM_KEYWORDS: Dict[str, List[tuple]] = {
    "impersonation": [
        ("bộ công an", 25),
        ("công an", 20),
        ("viện kiểm sát", 25),
        ("tòa án", 25),
        ("cơ quan điều tra", 25),
        ("cơ quan công an", 25),
        ("lệnh bắt", 25),
        ("truy nã", 25),
        ("phạt nguội", 20),
        ("cục thuế", 18),
        ("đại diện ngân hàng", 15),
        ("nợ xấu", 15),
    ],
    "phishing": [
        ("mã otp", 25),
        ("mật khẩu", 20),
        ("số thẻ", 15),
        ("mã cvv", 20),
        ("khóa tài khoản", 20),
        ("tài khoản bị khóa", 20),
        ("phong tỏa tài khoản", 25),
        ("chuyển khoản gấp", 20),
        ("chuyển tiền gấp", 20),
        ("chuyển tiền", 12),
        ("chuyển khoản", 10),
        ("xác minh ngay", 15),
        ("đăng nhập ngay", 15),
        ("cập nhật thông tin", 12),
        ("trúng thưởng", 20),
        ("vui lòng đăng nhập", 15),
        ("xác thực tài khoản", 15),
        ("xác minh tài khoản", 15),
        ("giao dịch bất thường", 18),
        ("nghi vấn giao dịch", 18),
        ("verify you're human", 12),
        ("security check", 8),
        ("access temporarily blocked", 20),
        ("failed verification attempts", 15),
        ("account suspended", 20),
        ("contact your hosting provider", 8),
        ("continue with google", 8),
        ("continue with facebook", 8),
        ("continue with apple", 8),
        ("continue with email", 10),
        ("verify your account", 15),
        ("verify your identity", 15),
    ],
    "fake_invoice": [
        ("nộp phạt", 20),
        ("thanh toán đơn hàng", 12),
        ("hóa đơn chưa thanh toán", 15),
        ("phí vận chuyển", 10),
        ("shipper", 10),
        ("đặt cọc", 15),
        ("tất toán", 12),
    ],
    "job_scam": [
        ("làm nhiệm vụ", 22),
        ("tiền hoa hồng", 20),
        ("hoa hồng", 14),
        ("cộng tác viên", 15),
        ("tuyển nhân viên", 15),
        ("làm việc tại nhà", 12),
        ("nạp tiền", 18),
        ("nhận tiền", 10),
        ("phí dịch vụ", 12),
    ],
    "urgent_account_threat": [
        ("ngay lập tức", 15),
        ("trong 24h", 15),
        ("trong vòng 24h", 15),
        ("trong 2 giờ", 15),
        ("bị trừ", 15),
        ("tài khoản của bạn", 10),
        ("nhấn vào", 10),
        ("dịch vụ tài chính", 10),
        ("sau 24h", 12),
        ("trong vòng 24 giờ", 15),
        ("tạm khóa", 15),
        ("bị khóa", 15),
    ],
}

_dynamic_cache = (0.0, {})


def _active_keywords() -> Dict[str, List[tuple]]:
    """Merge admin-managed rules with safe built-ins; database failure is non-fatal."""
    global _dynamic_cache
    now = time.monotonic()
    if _dynamic_cache[0] > now:
        dynamic = _dynamic_cache[1]
    else:
        dynamic: Dict[str, List[tuple]] = {}
        try:
            from backend.app.db.database import SessionLocal
            from backend.app.db.models import ScamKeyword
            db = SessionLocal()
            try:
                for row in db.query(ScamKeyword).all():
                    dynamic.setdefault(row.category, []).append((row.keyword, int(row.weight)))
            finally:
                db.close()
        except Exception:
            dynamic = {}
        _dynamic_cache = (now + 30, dynamic)
    merged = {category: list(values) for category, values in SCAM_KEYWORDS.items()}
    for category, values in dynamic.items():
        existing = {keyword for keyword, _weight in merged.get(category, [])}
        merged.setdefault(category, []).extend((keyword, weight) for keyword, weight in values if keyword not in existing)
    return merged

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

    for category, keywords in _active_keywords().items():
        for keyword, weight in keywords:
            normalized_keyword = _remove_diacritics(keyword)
            if normalized_keyword in normalized_text and not _only_negated_mentions(normalized_text, normalized_keyword):
                score += weight
                matched_terms.append(keyword)
                category_scores[category] = category_scores.get(category, 0) + weight

    # A sign-in surface by itself may be legitimate. Multiple authentication
    # prompts in an uploaded screenshot are still a meaningful phishing signal,
    # especially when the browser address/domain is not available for checking.
    auth_flow_terms = [
        "continue with google", "continue with facebook", "continue with apple",
        "continue with email", "sign in", "log in", "login", "dang nhap",
        "verify your account", "verify your identity", "xac minh tai khoan",
        "xac thuc tai khoan",
    ]
    auth_flow_hits = [term for term in auth_flow_terms if term in normalized_text]
    if len(auth_flow_hits) >= 2:
        score += 12
        matched_terms.append("biểu mẫu đăng nhập/xác thực")
        category_scores["phishing"] = category_scores.get("phishing", 0) + 12

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

    # Corroboration rules capture scam intent that individual keywords cannot:
    # an alleged authority requesting money, and a job requiring an upfront
    # payment.  The amount/payment cue is required to avoid flagging ordinary
    # recruitment posts or neutral mentions of public agencies.
    transfer_cues = ("chuyen tien", "chuyen khoan", "nop phat", "dong phi", "dat coc")
    if category_scores.get("impersonation", 0) >= 20 and any(cue in normalized_text for cue in transfer_cues):
        score += 20
        matched_terms.append("giả mạo cơ quan kèm yêu cầu chuyển tiền")
        category_scores["impersonation"] = category_scores.get("impersonation", 0) + 20

    job_cues = ("cong tac vien", "tuyen nhan vien", "lam nhiem vu", "lam viec tai nha", "hoa hong")
    upfront_payment = bool(re.search(r"(?:nap|dong|chuyen|coc)\D{0,20}\d[\d\.\,]{3,}", normalized_text)) or any(
        cue in normalized_text for cue in ("nap tien", "dong phi", "dat coc", "phi dich vu")
    )
    if upfront_payment and any(cue in normalized_text for cue in job_cues):
        score += 22
        matched_terms.append("việc làm yêu cầu nộp tiền trước")
        category_scores["job_scam"] = category_scores.get("job_scam", 0) + 22

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


def _only_negated_mentions(text: str, keyword: str) -> bool:
    """Ignore a keyword only when every mention is clearly preventive/negated."""
    positions = [match.start() for match in re.finditer(re.escape(keyword), text)]
    if not positions:
        return False
    negation_cues = (
        "khong bao gio", "tuyet doi khong", "khong duoc", "khong nen",
        "khong can", "khong yeu cau", "dung ", "tranh ",
    )
    educational_cues = ("canh bao an toan", "phong tranh lua dao", "khuyen cao")
    for position in positions:
        before = text[max(0, position - 65):position]
        clause = before.split(".")[-1].split(";")[-1]
        if not any(cue in clause for cue in negation_cues) and not (
            any(cue in before for cue in educational_cues) and "khong" in clause
        ):
            return False
    return True


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
