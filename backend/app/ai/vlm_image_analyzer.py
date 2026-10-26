"""Multimodal Reasoning & Vision Analysis for Scam Detection.

Designed for scientific research:
Supports either an external Vision-Language Model (Qwen2.5-VL / API)
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

MODEL_ID = os.getenv("VLM_MODEL_ID", "Qwen/Qwen2.5-VL-3B-Instruct")
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
        }


def _enabled() -> bool:
    return os.getenv("USE_VLM_ANALYZER", "false").strip().lower() in {"1", "true", "yes"}


def _load_model() -> tuple[Any, Any]:
    """Load Qwen lazily if enabled and hardware supports it."""
    global _model_cache, _processor_cache, _load_error
    if _model_cache is not None and _processor_cache is not None:
        return _model_cache, _processor_cache
    if _load_error:
        raise RuntimeError(_load_error)

    try:
        import torch
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

        if MODEL_DEVICE == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif MODEL_DEVICE in {"cpu", "cuda"}:
            device = MODEL_DEVICE
        else:
            raise ValueError("VLM_DEVICE chỉ nhận auto, cpu hoặc cuda.")

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("VLM_DEVICE=cuda nhưng PyTorch không nhận thấy GPU CUDA.")

        dtype = torch.float16 if device == "cuda" else torch.float32
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_ID, torch_dtype=dtype)
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


def _parse_response(response: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", response, flags=re.DOTALL)
    if not match:
        raise ValueError("Model không trả về JSON.")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON của model không phải object.")
    return data


def _prompt(ocr_text: str, qr_codes: list[str]) -> str:
    safe_ocr = ocr_text.strip()[:4000] or "(OCR chưa đọc được chữ)"
    safe_qr = "; ".join(qr_codes[:5]) or "(không có QR)"
    return f"""Bạn là lớp phân tích an toàn cho ảnh nghi ngờ lừa đảo tại Việt Nam.
Phân tích CHỈ những gì thật sự nhìn thấy trong ảnh. Không mở URL, không suy đoán
thông tin bị che và không khẳng định chắc chắn đây là lừa đảo nếu bằng chứng yếu.

Văn bản OCR đã đọc: {safe_ocr}
QR đã giải mã: {safe_qr}

Hãy xem ảnh và tìm bằng chứng cụ thể: mạo danh tổ chức/thương hiệu, biểu mẫu yêu
cầu mật khẩu/OTP/thông tin thanh toán, lời thúc giục hoặc đe dọa, yêu cầu chuyển
tiền, URL/QR/số điện thoại đáng ngờ, và dấu hiệu bố cục không nhất quán.

Chỉ trả về JSON hợp lệ, không thêm Markdown, theo đúng schema:
{{
  "verdict": "safe|suspicious|high_risk|insufficient_evidence",
  "confidence": 0.0,
  "risk_indicators": ["bằng chứng quan sát được"],
  "observed_text": ["đoạn chữ nhìn thấy quan trọng"],
  "reasoning": "giải thích ngắn bằng tiếng Việt",
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
) -> VlmImageResult:
    """Analyze image context using Qwen2.5-VL if enabled, else Multimodal CoT Reasoning Engine."""
    if not Path(image_path).is_file():
        return VlmImageResult(available=False, note="Không tìm thấy ảnh để gửi cho model ngữ cảnh.")

    # 1. If Qwen2.5-VL is explicitly enabled, attempt running it
    if _enabled():
        try:
            model, processor = _load_model()
            image = Image.open(image_path).convert("RGB")
            messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": _prompt(ocr_text, qr_codes or [])}]}]
            rendered_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[rendered_prompt], images=[image], padding=True, return_tensors="pt")
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
            return VlmImageResult(
                available=True,
                verdict=verdict,
                confidence=round(confidence, 3),
                risk_score=score_by_verdict[verdict],
                risk_indicators=_clean_string_list(data.get("risk_indicators")),
                observed_text=_clean_string_list(data.get("observed_text")),
                reasoning=str(data.get("reasoning", "")).strip()[:700],
                recommended_action=str(data.get("recommended_action", "")).strip()[:500],
                model_name=MODEL_ID,
                note="Điểm VLM là tín hiệu theo bằng chứng model nêu ra, không phải xác suất đã hiệu chuẩn.",
            )
        except Exception:
            pass  # Fallback to Multimodal CoT Reasoning Engine below

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
        note=cot_result.note,
        chain_of_thought=cot_result.chain_of_thought,
    )
