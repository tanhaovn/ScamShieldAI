"""Multimodal Reasoning & Vision Analysis for Scam Detection.

Designed for scientific research:
Supports an instruction-tuned local Vision-Language Model
or the built-in Multimodal Chain-of-Thought (CoT) Reasoning Engine
that synthesizes ResNet-18 visual predictions, ELA forensic signals,
OCR text semantics, and PhishVN URL risks into structured evidence.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from backend.app.ai.reasoning_engine import execute_multimodal_reasoning

MODEL_ID = os.getenv("VLM_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")
MODEL_DEVICE = os.getenv("VLM_DEVICE", "auto").strip().lower()
MAX_NEW_TOKENS = 420

_model_cache: Any = None
_processor_cache: Any = None
_load_error: str | None = None


@dataclass
class VlmImageResult:
    available: bool
    verdict: str = "unavailable"
    confidence: float = 0.0
    risk_score: int = 0
    risk_indicators: list[str] = field(default_factory=list)
    observed_text: list[str] = field(default_factory=list)
    reasoning: str = ""
    recommended_action: str = ""
    model_name: str = "Multimodal-CoT-Reasoning"
    note: str = ""
    chain_of_thought: list[str] = field(default_factory=list)
    explanation_source: str = "unavailable"
    explanation_items: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_indicators": self.risk_indicators,
            "observed_text": self.observed_text,
            "reasoning": self.reasoning,
            "recommended_action": self.recommended_action,
            "model_name": self.model_name,
            "note": self.note,
            "chain_of_thought": self.chain_of_thought,
            "explanation_source": self.explanation_source,
            "explanation_items": self.explanation_items,
        }


def _enabled() -> bool:
    return os.getenv("USE_VLM_ANALYZER", "false").strip().lower() in {"1", "true", "yes"}


def _load_model() -> tuple[Any, Any]:
    """Load the configured VLM lazily if enabled and hardware supports it."""
    global _model_cache, _processor_cache, _load_error
    if _model_cache is not None and _processor_cache is not None:
        return _model_cache, _processor_cache
    if _load_error:
        raise RuntimeError(_load_error)

    try:
        import torch
        from transformers import AutoModelForVision2Seq, AutoProcessor

        if MODEL_DEVICE == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif MODEL_DEVICE in {"cpu", "cuda"}:
            device = MODEL_DEVICE
        else:
            raise ValueError("VLM_DEVICE chỉ nhận auto, cpu hoặc cuda.")

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("VLM_DEVICE=cuda nhưng PyTorch không nhận thấy GPU CUDA.")

        dtype = torch.float16 if device == "cuda" else torch.float32
        model = AutoModelForVision2Seq.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            _attn_implementation="eager",
        )
        model.to(device)
        model.eval()
        _model_cache = model
        _processor_cache = AutoProcessor.from_pretrained(MODEL_ID)
        return _model_cache, _processor_cache
    except Exception as error:
        _load_error = str(error)
        raise RuntimeError(_load_error) from error


def _clean_string_list(value: Any, limit: int = 6) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text and text not in cleaned:
                cleaned.append(text[:300])
        if len(cleaned) >= limit:
            break
    return cleaned


def _clean_explanation_items(value: Any, limit: int = 6) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    cleaned: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        observation = str(item.get("observation", "")).strip()[:300]
        why_risky = str(item.get("why_risky", "")).strip()[:500]
        location = str(item.get("location", "")).strip()[:120]
        if observation and why_risky:
            cleaned.append(
                {
                    "observation": observation,
                    "why_risky": why_risky,
                    "location": location,
                }
            )
        if len(cleaned) >= limit:
            break
    return cleaned


def _parse_response(response: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", response, flags=re.DOTALL)
    if not match:
        raise ValueError("Model không trả về JSON.")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON của model không phải object.")
    return data


def _prompt(
    ocr_text: str,
    qr_codes: list[str],
    image_model_label: str,
    gradcam_focus_regions: list[str],
) -> str:
    safe_ocr = ocr_text.strip()[:4000] or "(OCR chưa đọc được chữ)"
    safe_qr = "; ".join(qr_codes[:5]) or "(không có QR)"
    safe_focus = "; ".join(gradcam_focus_regions[:3]) or "(chưa xác định)"
    return f"""Bạn là chuyên gia phân tích ảnh nghi ngờ lừa đảo tại Việt Nam.
Bạn nhận hai ảnh theo thứ tự: (1) ảnh gốc và, nếu có, (2) bản đồ nhiệt Grad-CAM
của bộ phân loại ResNet18. Hãy tự quan sát toàn bộ ảnh, đọc bố cục và liên kết các
chi tiết thành một kịch bản cụ thể. Không được chỉ lặp lại phần trăm dự đoán,
không được giải thích chung chung và không được kết luận chỉ vì xuất hiện một từ.

Grad-CAM chỉ cho biết vùng tác động tới đầu ra "{image_model_label}"; nó không tự
chứng minh lừa đảo. Các vùng mạnh được thuật toán định vị gần: {safe_focus}.

Văn bản OCR tham khảo (có thể sai, chỉ dùng để kiểm chứng điều nhìn thấy): {safe_ocr}
QR đã giải mã: {safe_qr}

Với từng bằng chứng, phải nêu đủ ba phần:
1. Nhìn thấy chi tiết cụ thể nào trong ảnh.
2. Chi tiết nằm ở khu vực nào.
3. Vì sao chi tiết đó kết hợp với các chi tiết khác tạo ra cơ chế lừa đảo
   (mồi nhử, yêu cầu hành động, áp lực, lợi ích cho kẻ gian hoặc hậu quả cho nạn nhân).

Nếu là ảnh đời thường như con chó, con mèo hoặc phong cảnh, hãy mô tả đúng đối
tượng và kết luận không đủ bằng chứng lừa đảo. Không biến OCR thành danh sách từ
khóa. Không mở URL, không suy đoán nội dung bị che.

Chỉ trả về JSON hợp lệ, không thêm Markdown, theo đúng schema:
{{
  "verdict": "safe|suspicious|high_risk|insufficient_evidence",
  "confidence": 0.0,
  "summary": "giải thích trực tiếp tại sao ảnh có hoặc không có dấu hiệu lừa đảo",
  "evidence": [
    {{
      "observation": "chi tiết cụ thể nhìn thấy",
      "location": "vị trí trong ảnh",
      "why_risky": "mối liên hệ và cơ chế rủi ro cụ thể"
    }}
  ],
  "observed_text": ["đoạn chữ nhìn thấy quan trọng"],
  "uncertainty": "điều model chưa thể xác minh từ ảnh",
  "recommended_action": "hành động an toàn ngắn bằng tiếng Việt"
}}"""


def analyze_image_context(
    image_path: str,
    *,
    ocr_text: str = "",
    qr_codes: list[str] | None = None,
    visual_flags: list[str] | None = None,
    image_model_probability: float | None = None,
    phishvn_url_score: int = 0,
    phishvn_predictions: list[dict[str, Any]] | None = None,
    gradcam_path: str = "",
    gradcam_focus_regions: list[str] | None = None,
    image_model_label: str = "unavailable",
) -> VlmImageResult:
    """Use a real VLM for semantic explanation; keep rules only for risk fallback."""
    if not Path(image_path).is_file():
        return VlmImageResult(available=False, note="Không tìm thấy ảnh để gửi cho model ngữ cảnh.")

    # 1. If a real VLM is explicitly enabled, attempt running it.
    if _enabled():
        try:
            model, processor = _load_model()
            image = Image.open(image_path).convert("RGB")
            images = [image]
            content: list[dict[str, Any]] = [{"type": "image"}]
            if gradcam_path and Path(gradcam_path).is_file():
                images.append(Image.open(gradcam_path).convert("RGB"))
                content.append({"type": "image"})
            content.append(
                {
                    "type": "text",
                    "text": _prompt(
                        ocr_text,
                        qr_codes or [],
                        image_model_label,
                        gradcam_focus_regions or [],
                    ),
                }
            )
            messages = [{"role": "user", "content": content}]
            rendered_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[rendered_prompt], images=images, padding=True, return_tensors="pt")
            inputs = inputs.to(model.device)
            generated = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
            new_tokens = generated[:, inputs.input_ids.shape[1]:]
            raw_response = processor.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
            data = _parse_response(raw_response)

            verdict = str(data.get("verdict", "insufficient_evidence")).strip().lower()
            if verdict not in {"safe", "suspicious", "high_risk", "insufficient_evidence"}:
                verdict = "insufficient_evidence"
            confidence = max(0.0, min(float(data.get("confidence", 0.0)), 1.0))
            score_by_verdict = {"safe": 10, "suspicious": 45, "high_risk": 75, "insufficient_evidence": 0}
            explanation_items = _clean_explanation_items(data.get("evidence"))
            summary = str(data.get("summary", "")).strip()[:900]
            uncertainty = str(data.get("uncertainty", "")).strip()[:400]
            risk_indicators = [item["observation"] for item in explanation_items]
            return VlmImageResult(
                available=True,
                verdict=verdict,
                confidence=round(confidence, 3),
                risk_score=score_by_verdict[verdict],
                risk_indicators=risk_indicators,
                observed_text=_clean_string_list(data.get("observed_text")),
                reasoning=summary,
                recommended_action=str(data.get("recommended_action", "")).strip()[:500],
                model_name=MODEL_ID,
                note=(
                    "Giải thích được sinh trực tiếp bởi Vision-Language Model từ ảnh gốc và Grad-CAM. "
                    + (f"Giới hạn: {uncertainty}" if uncertainty else "Kết quả cần được người dùng kiểm chứng.")
                ),
                explanation_source="vision_language_model",
                explanation_items=explanation_items,
            )
        except Exception as error:
            vlm_error = f"{type(error).__name__}: {error}"
    else:
        vlm_error = "USE_VLM_ANALYZER chưa được bật."

    # 2. Multimodal CoT Reasoning Engine (Always Available, Scientific XAI)
    cot_result = execute_multimodal_reasoning(
        ocr_text=ocr_text,
        qr_codes=qr_codes or [],
        visual_flags=visual_flags or [],
        image_model_probability=image_model_probability,
        phishvn_url_score=phishvn_url_score,
        phishvn_predictions=phishvn_predictions or [],
    )

    return VlmImageResult(
        available=True,
        verdict=cot_result.verdict,
        confidence=cot_result.confidence,
        risk_score=cot_result.risk_score,
        risk_indicators=cot_result.risk_indicators,
        observed_text=cot_result.observed_text,
        reasoning=cot_result.reasoning,
        recommended_action=cot_result.recommended_action,
        model_name=cot_result.model_name,
        note=(
            f"Chưa có giải thích AI thị giác: {vlm_error} "
            "Điểm ngữ cảnh hiện chỉ là kết quả dự phòng từ luật; giao diện không được trình bày nó như lời giải thích của AI."
        ),
        chain_of_thought=cot_result.chain_of_thought,
        explanation_source="rule_fallback",
        explanation_items=[],
    )
