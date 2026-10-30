"""Multimodal Chain-of-Thought (CoT) Reasoning Engine for Scam Detection.

Equipped with:
1. Domain Gating: Filters out natural/everyday photos (landscape, selfies, memes)
   to completely eliminate false positives.
2. Calibrated Multimodal Fusion: Only raises high alarm when visual features,
   text semantics, or URL signals correlate with known scam patterns.
3. Multi-tier Architecture: Scientific CoT explainability.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
import unicodedata
from typing import Any


def remove_vietnamese_accents(text: str) -> str:
    """Normalize Vietnamese text to non-accented lower characters for robust keyword matching."""
    nfkd = unicodedata.normalize("NFKD", text)
    stripped = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return stripped.replace("đ", "d").replace("Đ", "D").lower()


@dataclass
class ReasoningResult:
    available: bool
    verdict: str  # "safe" | "suspicious" | "high_risk" | "insufficient_evidence"
    confidence: float
    risk_score: int
    chain_of_thought: list[str] = field(default_factory=list)
    risk_indicators: list[str] = field(default_factory=list)
    observed_text: list[str] = field(default_factory=list)
    reasoning: str = ""
    recommended_action: str = ""
    model_name: str = "Multimodal-CoT-Reasoning-v2"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "chain_of_thought": self.chain_of_thought,
            "risk_indicators": self.risk_indicators,
            "observed_text": self.observed_text,
            "reasoning": self.reasoning,
            "recommended_action": self.recommended_action,
            "model_name": self.model_name,
            "note": self.note,
        }


# Targeted scam keyword dictionaries (Vietnamese context)
ORGANIZATION_KEYWORDS = [
    "bộ công an", "công an", "viện kiểm sát", "tòa án", "cục thuế",
    "bảo hiểm xã hội", "ngân hàng nhà nước", "vietcombank", "techcombank",
    "mbbank", "vietinbank", "bidv", "agribank", "vpbank", "tpbank",
    "vcb", "tcb", "mb", "viettel", "vnpt", "fpt", "shopee", "lazada", "tiktok"
]

URGENT_KEYWORDS = [
    "khóa tài khoản", "lệnh bắt", "truy nã", "phạt nguội", "trừ tiền",
    "đình chỉ", "vi phạm", "khẩn cấp", "ngay lập tức", "trong vòng 24h",
    "hoàn tất thủ tục", "phong tỏa tài khoản", "niêm phong"
]

FINANCIAL_ACTION_KEYWORDS = [
    "chuyển tiền", "nộp phạt", "mã otp", "mật khẩu", "số thẻ", "cvv",
    "đặt cọc", "phí bảo hiểm", "nhận quà", "trúng thưởng", "làm nhiệm vụ",
    "tiền hoa hồng", "nạp tiền", "số tài khoản", "stk"
]

SOURCE_CODE_SYNTAX = [
    "create table", "create database", "primary key", "auto_increment",
    "varchar", "select *", "insert into", "console.log", "import react",
    "public static void", "def ", "class ", "function(", "<?php"
]


def execute_multimodal_reasoning(
    *,
    ocr_text: str = "",
    qr_codes: list[str] | None = None,
    visual_flags: list[str] | None = None,
    image_model_probability: float | None = None,
    phishvn_url_score: int = 0,
    phishvn_predictions: list[dict[str, Any]] | None = None,
) -> ReasoningResult:
    """Execute multi-step Chain-of-Thought reasoning with Domain Gating."""
    qr_codes = qr_codes or []
    visual_flags = visual_flags or []
    phishvn_predictions = phishvn_predictions or []
    clean_text = ocr_text.strip().lower()
    clean_text_no_accents = remove_vietnamese_accents(clean_text)

    cot_steps: list[str] = []
    indicators: list[str] = []
    observed_snippets: list[str] = []

    def matches_keyword(kw: str) -> bool:
        kw_lower = kw.lower()
        if kw_lower in clean_text:
            return True
        kw_no_accents = remove_vietnamese_accents(kw_lower)
        return kw_no_accents in clean_text_no_accents

    # ---------------------------------------------------------
    # Bước 1: Trích xuất thực thể & Phân tích ngữ nghĩa (Semantic Analysis)
    # ---------------------------------------------------------
    found_orgs = [kw for kw in ORGANIZATION_KEYWORDS if matches_keyword(kw)]
    found_urgent = [kw for kw in URGENT_KEYWORDS if matches_keyword(kw)]
    found_actions = [kw for kw in FINANCIAL_ACTION_KEYWORDS if matches_keyword(kw)]

    has_suspicious_url = phishvn_url_score >= 40
    has_qr = len(qr_codes) > 0
    has_text_evidence = bool(found_orgs or found_urgent or found_actions)

    # ---------------------------------------------------------
    # BỘ LỌC ĐỜI THƯỜNG & MÃ NGUỒN (DOMAIN GATING)
    # ---------------------------------------------------------
    # Nếu là ảnh chụp code lập trình / cú pháp kỹ thuật:
    is_source_code = any(syntax in clean_text for syntax in SOURCE_CODE_SYNTAX)
    if is_source_code and not has_suspicious_url:
        return ReasoningResult(
            available=True,
            verdict="safe",
            confidence=0.98,
            risk_score=0,
            chain_of_thought=[
                "[Bộ lọc phân vùng - Source Code]: Phát hiện mã nguồn lập trình / cấu trúc câu lệnh kỹ thuật (SQL / Code).",
                "[Loại trừ an toàn]: Các từ khóa trùng tên thương hiệu (như tên bảng, tên biến) được bỏ qua, không tính là dấu hiệu lừa đảo.",
            ],
            risk_indicators=[],
            observed_text=[],
            reasoning="Hình ảnh là mã nguồn lập trình hoặc tài liệu kỹ thuật, hoàn toàn an toàn.",
            recommended_action="Nội dung kỹ thuật an toàn, không có thao tác cần cảnh báo.",
            model_name="Multimodal-CoT-Reasoning-v2 (Code-Aware)",
            note="Bộ lọc cú pháp mã nguồn tự động loại trừ cảnh báo giả cho ảnh lập trình.",
        )

    # Nếu ảnh KHÔNG CÓ chữ nhạy cảm, KHÔNG CÓ link độc hại, KHÔNG CÓ mã QR:
    # Đây là ảnh đời thường (phong cảnh, người, động vật, tài liệu thông thường).
    # Ta không để các mô hình thị giác bị nhiễu (Domain Shift) báo nhầm!
    if not has_text_evidence and not has_suspicious_url and not has_qr:
        return ReasoningResult(
            available=True,
            verdict="safe",
            confidence=0.95,
            risk_score=0,
            chain_of_thought=[
                "[Bộ lọc phân vùng - Domain Gating]: Ảnh không chứa văn bản yêu cầu tài chính, không có mã QR và không có liên kết đáng ngờ.",
                "[Đánh giá đời thường]: Ảnh được phân loại là hình ảnh đời thường/nội dung tự nhiên an toàn.",
            ],
            risk_indicators=[],
            observed_text=[],
            reasoning="Hình ảnh đời thường hoặc tài liệu thông thường, không phát hiện dấu hiệu lừa đảo.",
            recommended_action="Nội dung an toàn, không có thao tác cần cảnh báo.",
            model_name="Multimodal-CoT-Reasoning-v2 (Gated)",
            note="Cơ chế Domain Gating đã loại trừ nguy cơ dương tính giả đối với ảnh tự nhiên.",
        )

    # ---------------------------------------------------------
    # Bước 2: Phân tích Thị giác & Dấu vết Pháp y (Visual Forensics)
    # ---------------------------------------------------------
    visual_score = 0
    if image_model_probability is not None:
        prob_pct = round(image_model_probability * 100, 1)
        # Chỉ kích hoạt ảnh hưởng thị giác khi ResNet có độ tự tin cao
        if image_model_probability >= 0.70:
            cot_steps.append(
                f"[Thị giác - ResNet-18]: Mô hình nhận diện bố cục giao diện tương đồng với mẫu lừa đảo ({prob_pct}%)."
            )
            indicators.append(f"Mô hình thị giác cảnh báo nguy cơ ({prob_pct}%).")
            visual_score += 30
        elif image_model_probability >= 0.50:
            cot_steps.append(
                f"[Thị giác - ResNet-18]: Hình ảnh có một số nét tương đồng với giao diện mạo danh ({prob_pct}%)."
            )
            visual_score += 15

    # Lọc bỏ cờ EXIF thiếu (vì mạng xã hội luôn xóa EXIF)
    actionable_visual_flags = [
        f for f in visual_flags if "metadata exif" not in f.lower()
    ]
    for flag in actionable_visual_flags:
        cot_steps.append(f"[Pháp y ảnh]: {flag}")
        indicators.append(flag)
        visual_score += 20

    # ---------------------------------------------------------
    # Bước 3: Đánh giá Ngữ nghĩa Chi tiết
    # ---------------------------------------------------------
    text_score = 0
    if found_orgs:
        org_names = ", ".join(found_orgs[:3])
        cot_steps.append(f"[Ngữ nghĩa]: Đề cập danh tính tổ chức/cơ quan: {org_names}.")
        observed_snippets.append(f"Tổ chức/Thương hiệu: {org_names}")

    if found_urgent:
        urg_names = ", ".join(found_urgent[:3])
        cot_steps.append(f"[Ngữ nghĩa]: Xuất hiện yếu tố tâm lý thúc giục/đe dọa: {urg_names}.")
        indicators.append(f"Chiêu thức tạo áp lực tâm lý: {urg_names}")
        text_score += 25

    if found_actions:
        act_names = ", ".join(found_actions[:3])
        cot_steps.append(f"[Ngữ nghĩa]: Yêu cầu thao tác tài chính/bảo mật nhạy cảm: {act_names}.")
        indicators.append(f"Yêu cầu dữ liệu nhạy cảm: {act_names}")
        text_score += 35

    if has_qr:
        cot_steps.append(f"[Mã QR]: Phát hiện {len(qr_codes)} mã QR trong ảnh.")
        for qr in qr_codes[:2]:
            observed_snippets.append(f"Nội dung QR: {qr[:60]}")

    if phishvn_url_score >= 50:
        cot_steps.append(
            f"[URL/Domain]: Mô hình PhishVN phát hiện đường link có rủi ro cao ({phishvn_url_score}/100)."
        )
        indicators.append(f"URL độc hại/lừa đảo: điểm rủi ro {phishvn_url_score}/100")
        text_score += 40

    # ---------------------------------------------------------
    # Bước 4: Suy luận Logic mâu thuẫn (Core Reasoning)
    # ---------------------------------------------------------
    # 1. Mạo danh cơ quan công quyền
    is_gov_impersonation = any(kw in clean_text for kw in ["công an", "viện kiểm sát", "tòa án"]) and (found_urgent or found_actions)
    if is_gov_impersonation:
        cot_steps.append(
            "[Suy luận Logic - Cực kỳ nguy hiểm]: Cơ quan hành pháp Việt Nam không bao giờ làm việc, tống đạt văn bản, hay yêu cầu nộp phạt/chuyển tiền qua mạng xã hội/hình ảnh."
        )
        indicators.append("Mạo danh cơ quan bảo vệ pháp luật để đe dọa tống tiền.")
        text_score += 50

    # 2. Ngân hàng đòi mã OTP
    is_bank_otp = any(kw in clean_text for kw in ["vietcombank", "techcombank", "mbbank", "ngân hàng"]) and any(kw in clean_text for kw in ["mã otp", "mật khẩu", "số thẻ"])
    if is_bank_otp:
        cot_steps.append(
            "[Suy luận Logic - Cực kỳ nguy hiểm]: Ngân hàng không bao giờ yêu cầu khách hàng cung cấp mã OTP hoặc mật khẩu dưới bất kỳ hình thức nào."
        )
        indicators.append("Dấu hiệu chiếm quyền điều khiển tài khoản ngân hàng (đòi OTP/mật khẩu).")
        text_score += 50

    # ---------------------------------------------------------
    # Bước 5: Tính điểm tổng hợp có hiệu chuẩn (Calibrated Total)
    # ---------------------------------------------------------
    # Điểm chỉ cao khi có bằng chứng ngữ nghĩa/URL hoặc mâu thuẫn rõ ràng
    total_score = min(100, max(text_score, phishvn_url_score))
    if visual_score > 0 and (text_score >= 25 or phishvn_url_score >= 40):
        total_score = min(100, total_score + int(0.3 * visual_score))

    if total_score >= 60:
        verdict = "high_risk"
        action = "Tuyệt đối KHÔNG làm theo hướng dẫn, KHÔNG chuyển tiền, KHÔNG quét QR hoặc cung cấp mã OTP/mật khẩu. Hãy báo cáo cơ quan chức năng hoặc khóa thẻ ngân hàng ngay."
        reasoning_summary = "Hình ảnh có nhiều mâu thuẫn logic và dấu hiệu lừa đảo rõ ràng: mạo danh tổ chức, thúc ép tâm lý và đòi hỏi thông tin tài chính bảo mật."
    elif total_score >= 25:
        verdict = "suspicious"
        action = "Cần cẩn trọng xác minh độc lập qua tổng đài hoặc website chính thống trước khi thực hiện bất kỳ giao dịch nào."
        reasoning_summary = "Nội dung có một số dấu hiệu bất thường cần kiểm tra kỹ, chưa thể kết luận an toàn."
    else:
        verdict = "safe"
        action = "Chưa phát hiện dấu hiệu lừa đảo điển hình. Tuy nhiên vẫn nên tuân thủ các nguyên tắc an toàn số cơ bản."
        reasoning_summary = "Không phát hiện yếu tố mạo danh, thúc ép chuyển tiền hay dấu hiệu chỉnh sửa ảnh nghiêm trọng."

    confidence = round(min(0.98, max(0.65, total_score / 100.0 if total_score > 0 else 0.90)), 2)

    return ReasoningResult(
        available=True,
        verdict=verdict,
        confidence=confidence,
        risk_score=total_score,
        chain_of_thought=cot_steps,
        risk_indicators=indicators,
        observed_text=observed_snippets,
        reasoning=reasoning_summary,
        recommended_action=action,
        model_name="Multimodal-CoT-Reasoning-v2",
        note="Được suy luận tự động bởi mạng lai (Multimodal Hybrid CoT Engine: ResNet + Forensics + NLP).",
    )
