"""Multimodal Reasoning & Vision Analysis for Scam Detection.

Designed for scientific research:
Supports an instruction-tuned local Vision-Language Model
or the built-in Multimodal Chain-of-Thought (CoT) Reasoning Engine
that synthesizes ResNet-18 visual predictions, ELA forensic signals,
OCR text semantics, and PhishVN URL risks into structured evidence.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from backend.app.ai.reasoning_engine import execute_multimodal_reasoning

MODEL_ID = os.getenv("VLM_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")
MODEL_DEVICE = os.getenv("VLM_DEVICE", "auto").strip().lower()
LOCAL_FILES_ONLY = os.getenv("VLM_LOCAL_FILES_ONLY", "true").strip().lower() in {"1", "true", "yes"}
MAX_NEW_TOKENS = max(80, int(os.getenv("VLM_MAX_NEW_TOKENS", "140")))
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash").strip()

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


def _call_gemini_vision(image_paths: list[str], prompt: str, api_key: str) -> str:
    parts: list[dict[str, Any]] = [{"text": prompt}]
    for image_path in image_paths:
        mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        encoded = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        parts.append({"inline_data": {"mime_type": mime_type, "data": encoded}})

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_VISION_MODEL}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    body: dict[str, Any] | None = None
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            last_error = error
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)
    if body is None:
        raise RuntimeError(f"Gemini không phản hồi sau 3 lần thử: {last_error}")
    candidates = body.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini không trả về candidate.")
    response_parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [str(part.get("text", "")).strip() for part in response_parts if part.get("text")]
    result = "\n".join(part for part in text_parts if part).strip()
    if not result:
        raise RuntimeError("Gemini không trả về phần văn bản.")
    return result


def _has_causal_explanation(response: str) -> bool:
    normalized = response.lower()
    causal_markers = (
        "vì", "do đó", "nhằm", "khiến", "dụ", "áp lực", "chiếm", "đánh cắp",
        "hậu quả", "nạn nhân", "lừa đảo", "because", "therefore", "victim", "harm", "fraud",
    )
    return any(marker in normalized for marker in causal_markers)


def _gemini_structured_prompt(base_prompt: str) -> str:
    return base_prompt + """

Return only valid JSON, without Markdown, using this schema:
{
  "verdict": "safe|suspicious|high_risk|insufficient_evidence",
  "confidence": 0.0,
  "summary": "one direct Vietnamese conclusion",
  "evidence": [
    {
      "observation": "specific visible detail in Vietnamese",
      "location": "location in the image",
      "why_risky": "specific scam mechanism and possible harm"
    }
  ],
  "observed_text": ["important visible phrase"],
  "uncertainty": "what the image alone cannot verify",
  "recommended_action": "one short safe action in Vietnamese"
}
Use at most 3 evidence items. Confidence is confidence in the explanation, not
the ResNet probability."""


def _load_model() -> tuple[Any, Any]:
    """Load the configured VLM lazily if enabled and hardware supports it."""
    global _model_cache, _processor_cache, _load_error
    if _model_cache is not None and _processor_cache is not None:
        return _model_cache, _processor_cache
    if _load_error:
        raise RuntimeError(_load_error)

    try:
        import torch
        from huggingface_hub import snapshot_download
        from transformers import AutoModelForImageTextToText, AutoProcessor

        if MODEL_DEVICE == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif MODEL_DEVICE in {"cpu", "cuda"}:
            device = MODEL_DEVICE
        else:
            raise ValueError("VLM_DEVICE chỉ nhận auto, cpu hoặc cuda.")

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("VLM_DEVICE=cuda nhưng PyTorch không nhận thấy GPU CUDA.")

        # Passing the resolved snapshot directory is important on offline Windows
        # machines: some processors still issue a network HEAD request when they
        # receive a Hub model id, even with local_files_only=True.
        model_source = MODEL_ID
        if LOCAL_FILES_ONLY:
            model_source = snapshot_download(repo_id=MODEL_ID, local_files_only=True)

        dtype = torch.float16 if device == "cuda" else torch.float32
        model = AutoModelForImageTextToText.from_pretrained(
            model_source,
            dtype=dtype,
            low_cpu_mem_usage=True,
            _attn_implementation="eager",
            local_files_only=True if LOCAL_FILES_ONLY else False,
        )
        model.to(device)
        model.eval()
        _model_cache = model
        _processor_cache = AutoProcessor.from_pretrained(
            model_source,
            local_files_only=True if LOCAL_FILES_ONLY else False,
        )
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
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    # Small local VLMs follow a short line protocol more reliably than a nested
    # JSON schema. This is still the model's own visual explanation; no OCR rule
    # sentences are inserted here.
    parsed: dict[str, Any] = {"evidence": [], "observed_text": []}
    for raw_line in response.splitlines():
        line = raw_line.strip().lstrip("-*• ")
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().upper().replace(" ", "_")
        value = value.strip()
        if key == "VERDICT":
            parsed["verdict"] = value.lower()
        elif key == "CONFIDENCE":
            number = re.search(r"\d+(?:[.,]\d+)?", value)
            if number:
                confidence = float(number.group(0).replace(",", "."))
                parsed["confidence"] = confidence / 100 if confidence > 1 else confidence
        elif key == "SUMMARY":
            parsed["summary"] = value
        elif key.startswith("EVIDENCE"):
            parts = [part.strip() for part in value.split("||")]
            if len(parts) >= 3 and parts[0] and parts[2]:
                parsed["evidence"].append(
                    {"observation": parts[0], "location": parts[1], "why_risky": " || ".join(parts[2:])}
                )
        elif key == "TEXT":
            parsed["observed_text"].append(value)
        elif key == "UNCERTAINTY":
            parsed["uncertainty"] = value
        elif key == "ACTION":
            parsed["recommended_action"] = value

    if parsed.get("summary") or parsed["evidence"]:
        return parsed

    cleaned = response.strip()
    if cleaned:
        return {
            "verdict": "insufficient_evidence",
            "confidence": 0.0,
            "summary": cleaned,
            "evidence": [
                {
                    "observation": "Phân tích trực tiếp toàn bộ ảnh",
                    "location": "Toàn bộ ảnh",
                    "why_risky": cleaned,
                }
            ],
            "uncertainty": "Mô hình không trả lời đúng cấu trúc nên chưa tách riêng được từng bằng chứng.",
        }
    raise ValueError("Model không trả về nội dung.")


def _prompt(
    ocr_text: str,
    qr_codes: list[str],
    image_model_label: str,
    gradcam_focus_regions: list[str],
) -> str:
    safe_ocr = ocr_text.strip()[:2200] or "(OCR chưa đọc được chữ)"
    safe_qr = "; ".join(qr_codes[:5]) or "(không có QR)"
    safe_focus = "; ".join(gradcam_focus_regions[:3]) or "(chưa xác định)"
    return f"""Look at the original image and its optional Grad-CAM heatmap. Explain in
Vietnamese why this exact image may be an online scam. Do not transcribe the
message and do not list isolated keywords. Connect the claimed sender, the
threat or bait, the action requested from the victim, and the possible harm.
For each reason say what is visible, where it is, and why it is risky. If this
is an ordinary real-life photo, say there is not enough scam evidence. Write
2 or 3 short, specific Vietnamese bullet points followed by one conclusion.

The classifier label is {image_model_label}; strongest Grad-CAM areas are
{safe_focus}. These are hints, not proof. OCR is only an imperfect reading aid:
{safe_ocr}
Decoded QR: {safe_qr}"""


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
            image_paths = [image_path]
            if gradcam_path and Path(gradcam_path).is_file():
                image_paths.append(gradcam_path)
            analysis_prompt = _prompt(
                ocr_text,
                qr_codes or [],
                image_model_label,
                gradcam_focus_regions or [],
            )

            gemini_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
            if gemini_key:
                raw_response = _call_gemini_vision(
                    image_paths,
                    _gemini_structured_prompt(analysis_prompt),
                    gemini_key,
                )
                active_model_name = GEMINI_VISION_MODEL
            else:
                model, processor = _load_model()
                images = [Image.open(path).convert("RGB") for path in image_paths]
                content: list[dict[str, Any]] = [{"type": "image"} for _ in images]
                content.append({"type": "text", "text": analysis_prompt})
                messages = [{"role": "user", "content": content}]
                rendered_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[rendered_prompt], images=images, padding=True, return_tensors="pt")
                inputs = inputs.to(model.device)
                generated = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
                new_tokens = generated[:, inputs.input_ids.shape[1]:]
                raw_response = processor.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
                active_model_name = MODEL_ID
                if not _has_causal_explanation(raw_response):
                    raise ValueError(
                        "Mô hình cục bộ chỉ chép lại nội dung ảnh, chưa tạo được giải thích nguyên nhân. "
                        "Hãy cấu hình GEMINI_API_KEY để dùng mô hình thị giác mạnh hơn."
                    )
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
                model_name=active_model_name,
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
