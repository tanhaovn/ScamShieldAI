"""Download and validate the configured local vision-language model."""
from __future__ import annotations

import os

from transformers import AutoModelForImageTextToText, AutoProcessor


MODEL_ID = os.getenv("VLM_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")


def main() -> None:
    print(f"Caching VLM: {MODEL_ID}", flush=True)
    AutoProcessor.from_pretrained(MODEL_ID)
    AutoModelForImageTextToText.from_pretrained(
        MODEL_ID,
        low_cpu_mem_usage=True,
        _attn_implementation="eager",
    )
    print("VLM cache is ready.", flush=True)


if __name__ == "__main__":
    main()
