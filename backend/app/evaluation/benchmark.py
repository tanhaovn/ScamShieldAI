"""Small, auditable benchmark used by the admin quality dashboard.

This suite is intentionally kept in source control.  It is not a claim of
real-world accuracy; it is a regression gate that catches detector changes
which break representative Vietnamese scam and benign examples.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone


BENCHMARK_CASES = (
    {"id": "safe-chat", "kind": "text", "expected": "an_toan", "content": "Hẹn bạn 8 giờ tối nay đi uống cà phê nhé."},
    {"id": "safe-warning", "kind": "text", "expected": "an_toan", "content": "Cảnh báo an toàn: không bao giờ cung cấp mã OTP và không chuyển tiền cho người lạ."},
    {"id": "safe-maintenance", "kind": "text", "expected": "an_toan", "content": "Hệ thống bảo trì lúc 01:00. Bạn không cần đăng nhập hay cung cấp mật khẩu."},
    {"id": "safe-google", "kind": "url", "expected": "an_toan", "content": "https://www.google.com/"},
    {"id": "safe-microsoft", "kind": "url", "expected": "an_toan", "content": "https://www.microsoft.com/"},
    {"id": "safe-apple", "kind": "url", "expected": "an_toan", "content": "https://www.apple.com/"},
    {"id": "review-shortener", "kind": "url", "expected": "nghi_ngo", "content": "https://bit.ly/kiem-tra-tai-khoan"},
    {"id": "review-ip-login", "kind": "url", "expected": "nghi_ngo", "content": "http://192.0.2.10/login"},
    {"id": "danger-otp", "kind": "text", "expected": "nguy_hiem", "content": "Tài khoản bị khóa. Đăng nhập ngay và gửi mã OTP để xác minh tài khoản trong 2 giờ."},
    {"id": "danger-police", "kind": "text", "expected": "nguy_hiem", "content": "Bộ Công an yêu cầu chuyển khoản gấp 20 triệu để phục vụ điều tra."},
    {"id": "danger-job", "kind": "text", "expected": "nguy_hiem", "content": "Tuyển cộng tác viên online lương cao. Nạp 500.000 đồng để làm nhiệm vụ và nhận hoa hồng ngay."},
    {"id": "danger-brand-domain", "kind": "url", "expected": "nguy_hiem", "content": "https://google.verify-account-security.top/login"},
    # Punycode is a structural warning, not proof of abuse; without an
    # independent threat-list/content match the calibrated outcome is review.
    {"id": "review-punycode", "kind": "url", "expected": "nghi_ngo", "content": "https://xn--googl-fsa.com/login"},
)

LABELS = ("an_toan", "nghi_ngo", "nguy_hiem")


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def run_detector_benchmark(analyzer: Callable[[str], dict]) -> dict:
    """Run the checked-in cases and return exact and binary quality metrics."""
    rows: list[dict] = []
    matrix = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
    for case in BENCHMARK_CASES:
        result = analyzer(case["content"])
        actual = case["expected"]
        predicted = result.get("risk_level", "an_toan")
        if predicted not in LABELS:
            predicted = "an_toan"
        matrix[actual][predicted] += 1
        rows.append({
            "id": case["id"],
            "kind": case["kind"],
            "content": case["content"],
            "expected": actual,
            "actual": predicted,
            "score": int(result.get("risk_score") or 0),
            "passed": actual == predicted,
        })

    per_class: dict[str, dict] = {}
    f1_values: list[float] = []
    for label in LABELS:
        true_positive = matrix[label][label]
        false_positive = sum(matrix[other][label] for other in LABELS if other != label)
        false_negative = sum(matrix[label][other] for other in LABELS if other != label)
        precision = _safe_div(true_positive, true_positive + false_positive)
        recall = _safe_div(true_positive, true_positive + false_negative)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        f1_values.append(f1)
        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(matrix[label].values()),
        }

    # Binary scam detection treats both review and danger as a positive alert.
    tn = matrix["an_toan"]["an_toan"]
    fp = matrix["an_toan"]["nghi_ngo"] + matrix["an_toan"]["nguy_hiem"]
    fn = matrix["nghi_ngo"]["an_toan"] + matrix["nguy_hiem"]["an_toan"]
    tp = len(rows) - tn - fp - fn
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    binary_f1 = _safe_div(2 * precision * recall, precision + recall)
    passed = sum(row["passed"] for row in rows)

    return {
        "suite": "vietnamese-scam-regression-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "accuracy": round(_safe_div(passed, len(rows)), 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "binary": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(binary_f1, 4),
            "false_alarm_rate": round(_safe_div(fp, fp + tn), 4),
        },
        "labels": list(LABELS),
        "confusion_matrix": matrix,
        "per_class": per_class,
        "rows": rows,
    }
