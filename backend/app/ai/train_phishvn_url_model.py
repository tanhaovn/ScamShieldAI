"""Retrain the PhishVN HistGradientBoosting URL classifier.

By default this follows the dataset's published benchmark protocol: use the
official split and only gold/silver rows. The generated model is preferred by
the runtime over the reference model bundled with the dataset.

Run:
    python -m backend.app.ai.train_phishvn_url_model
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import warnings
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(min(os.cpu_count() or 1, 8)))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

from backend.app.ai.phishvn_url_model import FEATURE_NAMES, LOCAL_MODEL_PATH, PHISHVN_ROOT


DEFAULT_DATASET = PHISHVN_ROOT / "data" / "vn_compphish.csv"


def load_split(dataset_path: Path, split: str, include_bronze: bool) -> tuple[np.ndarray, np.ndarray]:
    features: list[list[float]] = []
    labels: list[int] = []
    with dataset_path.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["split"] != split:
                continue
            if not include_bronze and row["tier"] not in {"gold", "silver"}:
                continue
            features.append([float(row[name]) for name in FEATURE_NAMES])
            labels.append(int(row["label"]))
    return np.asarray(features, dtype=np.float64), np.asarray(labels, dtype=np.int64)


def train(dataset_path: Path, output_path: Path, include_bronze: bool = False) -> dict[str, float | int]:
    train_x, train_y = load_split(dataset_path, "train", include_bronze)
    test_x, test_y = load_split(dataset_path, "test", include_bronze)
    if not len(train_y) or not len(test_y):
        raise SystemExit("Không tìm thấy dữ liệu train/test phù hợp trong PhishVN.")

    model = HistGradientBoostingClassifier(class_weight="balanced", random_state=0)
    model.fit(train_x, train_y)
    # Preserve feature-order validation in the inference module without a pandas dependency.
    model.feature_names_in_ = np.asarray(FEATURE_NAMES, dtype=object)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names",
            category=UserWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message="Could not find the number of physical cores.*",
            category=UserWarning,
        )
        probabilities = model.predict_proba(test_x)[:, list(model.classes_).index(1)]
    predictions = (probabilities >= 0.5).astype(np.int64)
    metrics = {
        "n_train": int(len(train_y)),
        "n_test": int(len(test_y)),
        "f1": round(float(f1_score(test_y, predictions)), 4),
        "precision": round(float(precision_score(test_y, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(test_y, predictions, zero_division=0)), 4),
        "pr_auc": round(float(average_precision_score(test_y, probabilities)), 4),
        "roc_auc": round(float(roc_auc_score(test_y, probabilities)), 4),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(json.dumps({"model": str(output_path), **metrics}, ensure_ascii=False))
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=LOCAL_MODEL_PATH)
    parser.add_argument(
        "--include-bronze",
        action="store_true",
        help="Dùng cả nhãn bronze; mặc định chỉ dùng gold/silver theo benchmark chính thức.",
    )
    arguments = parser.parse_args()
    train(arguments.dataset, arguments.output, arguments.include_bronze)
