from backend.app.evaluation.benchmark import LABELS, run_detector_benchmark
from backend.app.main import _analyze_content_payload, health_check


def test_live_detector_regression_suite_has_no_known_failures():
    result = run_detector_benchmark(_analyze_content_payload)

    assert result["failed"] == 0, [row for row in result["rows"] if not row["passed"]]
    assert result["binary"]["false_positive"] == 0
    assert result["binary"]["false_negative"] == 0
    assert set(result["confusion_matrix"]) == set(LABELS)


def test_health_exposes_traceable_runtime_version():
    result = health_check()

    assert result["status"] == "ok"
    assert result["app_version"]
    assert result["git_commit"]
    assert result["services"]["database"] in {"sqlite", "mysql"}
