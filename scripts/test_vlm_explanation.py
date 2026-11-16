"""Smoke-test the visual AI explanation on one local image."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.ai.vlm_image_analyzer import analyze_image_context
from backend.app.ocr.ocr_service import extract_text_and_boxes


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    image_path = Path(sys.argv[1])
    print("[1/3] OCR...", flush=True)
    ocr_text, _words = extract_text_and_boxes(image_path)
    print("[2/3] ResNet18 + Grad-CAM...", flush=True)
    image_result = analyze_phishing_image(str(image_path))
    print("[3/3] Vision-Language Model...", flush=True)
    result = analyze_image_context(
        str(image_path),
        ocr_text=ocr_text,
        image_model_probability=image_result.probability,
        gradcam_path=image_result.gradcam_path,
        gradcam_focus_regions=image_result.gradcam_focus_regions or [],
        image_model_label=image_result.label,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
