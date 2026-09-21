"""Build a user-facing, structured explanation from all analysis layers."""
from __future__ import annotations

from typing import Any


LEVEL_LABELS = {
    "an_toan": "An toàn tương đối",
    "nghi_ngo": "Cần kiểm tra thêm",
    "nguy_hiem": "Nguy hiểm",
}


def _score_status(score: int) -> tuple[str, str]:
    if score >= 60:
        return "danger", "Nguy hiểm"
    if score >= 25:
        return "warning", "Nghi ngờ"
    return "safe", "Rủi ro thấp"


def _component(key: str, title: str, score: int, summary: str, findings: list[str]) -> dict[str, Any]:
    status, status_label = _score_status(score)
    return {
        "key": key,
        "title": title,
        "score": score,
        "status": status,
        "status_label": status_label,
        "summary": summary,
        "findings": findings,
    }


def build_analysis_explanation(
    *,
    extracted_text: str,
    text_result: Any,
    phishvn_result: Any,
    visual_result: Any,
    image_model_result: Any,
    image_model_score: int,
    combined_score: int,
    combined_level: str,
) -> tuple[str, dict[str, Any]]:
    """Return a readable plain-text explanation and a structured UI payload."""
    components: list[dict[str, Any]] = []

    if not extracted_text.strip():
        text_summary = "OCR không đọc được chữ, nên lớp phân tích nội dung chưa có đủ dữ liệu."
        text_findings = ["Hãy dùng ảnh rõ nét hơn, chụp thẳng và tránh lóa."]
    elif text_result.highlighted_terms:
        terms = ", ".join(text_result.highlighted_terms[:8])
        text_summary = f"Phát hiện {len(text_result.highlighted_terms)} cụm từ hoặc mẫu đáng chú ý."
        text_findings = [f"Từ/cụm bị đánh dấu: {terms}."]
        if text_result.scam_type != "none":
            text_findings.append(f"Nhóm nội dung gần nhất: {text_result.scam_type}.")
    else:
        text_summary = "OCR đọc được nội dung nhưng luật từ khóa chưa tìm thấy dấu hiệu mạnh."
        text_findings = ["Không phát hiện từ khóa lừa đảo đã biết trong Risk Engine."]
    components.append(
        _component(
            "text",
            "Nội dung OCR",
            int(text_result.risk_score),
            text_summary,
            text_findings,
        )
    )

    if phishvn_result.predictions:
        top_url = phishvn_result.predictions[0]
        url_summary = (
            f"PhishVN tìm thấy {len(phishvn_result.predictions)} URL/domain; "
            f"đáng chú ý nhất là {top_url.url}."
        )
        url_findings = [
            f"Điểm mô hình của {top_url.url}: {top_url.probability * 100:.1f}% "
            f"({top_url.label})."
        ]
        url_findings.extend(top_url.suspicious_signals)
    else:
        url_summary = "Không có URL/domain trong phần chữ OCR để PhishVN kiểm tra."
        url_findings = [
            "PhishVN chỉ phân tích cấu trúc URL; nó không phải model hiểu toàn bộ câu tiếng Việt."
        ]
    components.append(
        _component(
            "url",
            "URL PhishVN",
            int(phishvn_result.risk_score),
            url_summary,
            url_findings,
        )
    )

    visual_flags = list(visual_result.flags[:6]) if visual_result.flags else []
    if visual_flags:
        visual_summary = "Đã kiểm tra metadata và dấu hiệu chỉnh sửa trên ảnh."
    else:
        visual_summary = "Không phát hiện dấu hiệu hình ảnh đáng chú ý."
        visual_flags = ["EXIF/ELA/deepfake heuristic không tạo cảnh báo."]
    components.append(
        _component(
            "visual",
            "Dấu hiệu hình ảnh",
            int(visual_result.visual_score),
            visual_summary,
            visual_flags,
        )
    )

    if image_model_result.available:
        image_summary = "Model ResNet đã tham gia phân loại ảnh phishing/legitimate."
        image_findings = [image_model_result.explanation]
        components.append(
            _component(
                "image_model",
                "Model phân loại ảnh",
                image_model_score,
                image_summary,
                image_findings,
            )
        )

    strongest = max(components, key=lambda item: item["score"])
    level_label = LEVEL_LABELS.get(combined_level, combined_level)
    if combined_level == "nguy_hiem":
        headline = "Có tín hiệu rủi ro mạnh; không nên thực hiện yêu cầu trong ảnh."
    elif combined_level == "nghi_ngo":
        headline = "Có dấu hiệu cần xác minh trước khi bấm link hoặc giao dịch."
    else:
        headline = "Chưa thấy tín hiệu rủi ro mạnh, nhưng kết quả không bảo đảm an toàn tuyệt đối."

    reason = (
        f"Nguồn đóng góp lớn nhất là {strongest['title']} "
        f"({strongest['score']}/100 – {strongest['status_label'].lower()})."
    )
    breakdown = {
        "verdict": {
            "level": combined_level,
            "label": level_label,
            "score": combined_score,
            "headline": headline,
            "reason": reason,
        },
        "components": components,
        "score_method": (
            "Điểm tổng hợp ưu tiên tín hiệu có rủi ro cao nhất và chỉ cộng thêm một phần "
            "tín hiệu hỗ trợ từ các lớp còn lại; đây là điểm cảnh báo, không phải xác suất chắc chắn."
        ),
        "limitations": [
            "OCR có thể đọc sai khi ảnh mờ, chữ nhỏ hoặc bị che.",
            "PhishVN nhận diện URL phishing/abuse, không tự hiểu toàn bộ ngữ nghĩa tin nhắn.",
            "Kết quả cần được đối chiếu với website hoặc tổng đài chính thức.",
        ],
    }

    component_lines = [
        f"- {item['title']} ({item['score']}/100): {item['summary']}"
        for item in components
    ]
    plain_text = "\n".join(
        [
            f"KẾT LUẬN: {level_label} ({combined_score}/100). {headline}",
            f"LÝ DO CHÍNH: {reason}",
            "CHI TIẾT:",
            *component_lines,
            "LƯU Ý: Điểm số là tín hiệu hỗ trợ ra quyết định, không phải bằng chứng chắc chắn.",
        ]
    )
    return plain_text, breakdown
