"""Create a manifest template for the source-aware image split.

This script does not guess whether an image is public, synthetic, or
anonymized. Fill those fields in manually before training.
"""
import argparse
import csv
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def create_manifest(dataset_dir: Path, output_path: Path):
    rows = []
    for label in ("legitimate", "phishing"):
        label_dir = dataset_dir / label
        if not label_dir.is_dir():
            continue
        for image_path in sorted(label_dir.rglob("*")):
            if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
                rows.append(
                    {
                        "path": image_path.relative_to(dataset_dir).as_posix(),
                        "label": label,
                        "source": "FILL_ME",
                        "template_id": image_path.parent.name or "FILL_ME",
                        "split": "FILL_ME",
                    }
                )
    if not rows:
        raise SystemExit(f"Không tìm thấy ảnh trong {dataset_dir}.")
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["path", "label", "source", "template_id", "split"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {len(rows)} rows at {output_path}. Fill source/template_id/split.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("phishing_dataset"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    create_manifest(args.dataset, args.output or args.dataset / "manifest.csv")