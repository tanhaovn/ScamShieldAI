"""Run the end-to-end image detector against the checked-in labeled samples."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.main import _analyze_content_payload  # noqa: E402
from backend.app.ocr.ocr_service import extract_text_and_boxes  # noqa: E402
from backend.app.visual.qr_analysis import decode_qr_codes  # noqa: E402


SAMPLES = ROOT / "test_samples"


def main() -> int:
    rows: list[dict] = []
    for expected, folder in (("an_toan", "an_toan_safe"), ("nguy_hiem", "lua_dao_scam")):
        for path in sorted((SAMPLES / folder).glob("*")):
            text, _boxes = extract_text_and_boxes(str(path))
            payload = _analyze_content_payload(
                text,
                image_path=str(path),
                qr_codes=decode_qr_codes(str(path)),
            )
            rows.append(
                {
                    "file": path.name,
                    "expected": expected,
                    "status": 200,
                    "level": payload.get("risk_level"),
                    "score": payload.get("risk_score"),
                    "text": (payload.get("extracted_text") or "")[:120].replace("\n", " "),
                    "text_score": payload.get("text_risk_score"),
                    "url_score": payload.get("phishvn_url_risk_score"),
                    "image_score": payload.get("image_model_score"),
                    "visual_score": payload.get("visual_risk_score"),
                    "vlm_score": (payload.get("vlm_analysis") or {}).get("risk_score"),
                    "vlm_verdict": (payload.get("vlm_analysis") or {}).get("verdict"),
                }
            )

    def is_correct(row: dict) -> bool:
        if row["expected"] == "an_toan":
            return row["level"] == "an_toan"
        return row["level"] in {"nghi_ngo", "nguy_hiem"}

    correct = sum(is_correct(row) for row in rows)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"detection_accuracy={correct}/{len(rows)}")
    return 0 if correct == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
