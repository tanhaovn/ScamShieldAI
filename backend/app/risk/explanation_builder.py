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
    vlm_result: Any = None,
    combined_score: int,
    combined_level: str,
    include_visual: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Return a readable plain-text explanation and a structured UI payload."""
    components: list[dict[str, Any]] = []
    content_label = "OCR" if include_visual else "Nội dung"
    scam_type_labels = {
        "phishing": "giả mạo để lấy thông tin",
        "phishing_url": "đường link có dấu hiệu giả mạo",
        "impersonation": "mạo danh cơ quan hoặc tổ chức",
        "fake_invoice": "hóa đơn hoặc yêu cầu thanh toán giả",
        "job_scam": "lừa đảo tuyển dụng, việc làm",
        "urgent_account_threat": "đe dọa khóa hoặc trừ tiền tài khoản",
    }

    if not extracted_text.strip():
        text_summary = f"{content_label} không có chữ để lớp phân tích nội dung xử lý."
        text_findings = (["Hãy dùng ảnh rõ nét hơn, chụp thẳng và tránh lóa."] if include_visual else ["Hãy nhập thêm nội dung để hệ thống có đủ dữ liệu phân tích."])
    elif text_result.highlighted_terms:
        terms = ", ".join(text_result.highlighted_terms[:8])
        text_summary = f"Phát hiện {len(text_result.highlighted_terms)} cụm từ hoặc mẫu đáng chú ý."
        text_findings = [f"Từ/cụm bị đánh dấu: {terms}."]
        if text_result.scam_type != "none":
            readable_type = scam_type_labels.get(text_result.scam_type, "cần kiểm tra thêm")
            text_findings.append(f"Nội dung gần giống nhóm: {readable_type}.")
    else:
        text_summary = f"{content_label} đã được đọc nhưng luật từ khóa chưa tìm thấy dấu hiệu mạnh."
        text_findings = ["Không phát hiện từ khóa lừa đảo đã biết trong Risk Engine."]
    components.append(
        _component(
            "text",
            "Nội dung văn bản",
            int(text_result.risk_score),
            text_summary,
            text_findings,
        )
    )

    if phishvn_result.predictions:
        top_url = phishvn_result.predictions[0]
        url_summary = (
            f"Tìm thấy {len(phishvn_result.predictions)} đường link; "
            f"đáng chú ý nhất là {top_url.url}."
        )
        url_findings = [
            f"Mức độ đáng ngờ của {top_url.url}: {top_url.probability * 100:.1f}%."
        ]
        url_findings.extend(top_url.suspicious_signals)
    else:
        url_summary = "Không tìm thấy đường link trong nội dung này."
        url_findings = [
            "PhishVN chỉ phân tích cấu trúc URL; nó không phải model hiểu toàn bộ câu tiếng Việt."
        ]
    components.append(
        _component(
            "url",
            "Đường link trong nội dung",
            int(phishvn_result.risk_score),
            url_summary,
            url_findings,
        )
    )

    if include_visual:
        visual_flags = list(visual_result.flags[:6]) if visual_result.flags else []
        if visual_flags:
            visual_summary = "Đã kiểm tra metadata và dấu hiệu chỉnh sửa trên ảnh."
        else:
            visual_summary = "Không phát hiện dấu hiệu hình ảnh đáng chú ý."
            visual_flags = ["EXIF/ELA/deepfake heuristic không tạo cảnh báo."]
        components.append(
            _component(
                "visual",
                "Dấu hiệu chỉnh sửa ảnh",
                int(visual_result.visual_score),
                visual_summary,
                visual_flags,
            )
        )

    if include_visual and image_model_result.available:
        image_summary = "Model ResNet đã tham gia phân loại ảnh phishing/legitimate."
        image_findings = [image_model_result.explanation]
        components.append(
            _component(
                "image_model",
                "So sánh với mẫu ảnh lừa đảo",
                image_model_score,
                image_summary,
                image_findings,
            )
        )

    if include_visual and vlm_result and getattr(vlm_result, "available", False):
        verdict_labels = {
            "safe": "rủi ro thấp",
            "suspicious": "cần kiểm tra thêm",
            "high_risk": "nguy hiểm",
            "insufficient_evidence": "chưa đủ bằng chứng",
        }
        vlm_findings = list(vlm_result.risk_indicators[:5])
        if vlm_result.reasoning:
            vlm_findings.insert(0, vlm_result.reasoning)
        if not vlm_findings:
            vlm_findings = ["Model không nêu được bằng chứng hình ảnh cụ thể."]
        components.append(
            _component(
                "vlm_context",
                "AI hiểu ngữ cảnh ảnh",
                int(vlm_result.risk_score),
                f"{vlm_result.model_name} đánh giá: {verdict_labels.get(vlm_result.verdict, vlm_result.verdict)}.",
                vlm_findings,
            )
        )

    strongest = max(components, key=lambda item: item["score"])
    level_label = LEVEL_LABELS.get(combined_level, combined_level)
    if combined_level == "nguy_hiem":
        headline = "Có tín hiệu rủi ro mạnh; không nên thực hiện yêu cầu trong nội dung này."
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
        "limitations": (
            ["OCR có thể đọc sai khi ảnh mờ, chữ nhỏ hoặc bị che."]
            if include_visual else []
        ) + [
            "PhishVN nhận diện URL phishing/abuse, không tự hiểu toàn bộ ngữ nghĩa tin nhắn.",
            "Điểm từ AI hiểu ngữ cảnh ảnh là tín hiệu hỗ trợ, không phải xác suất đã được hiệu chuẩn.",
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
