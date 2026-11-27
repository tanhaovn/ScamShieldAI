from fastapi.testclient import TestClient
from PIL import Image

from backend.app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_SEED_ENABLED
from backend.app.main import app


def test_check_image_runs_without_mysql(tmp_path):
    image_path = tmp_path / "sample.jpg"
    image = Image.new("RGB", (128, 128), color=(255, 255, 255))
    image.save(image_path)

    with TestClient(app) as client:
        with image_path.open("rb") as f:
            response = client.post(
                "/check-image",
                files={"file": ("sample.jpg", f, "image/jpeg")},
                data={"user_id": 1},
            )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "risk_score" in payload
    assert "risk_level" in payload
    assert payload["risk_level"] in {"an_toan", "nghi_ngo", "nguy_hiem"}


def test_configured_admin_is_seeded_on_startup():
    assert ADMIN_SEED_ENABLED, "Test yêu cầu ADMIN_EMAIL và ADMIN_PASSWORD được cấu hình"
    with TestClient(app) as client:
        login = client.post(
            "/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        assert login.status_code == 200, login.text
        assert login.json()["user"]["role"] == "admin"


def test_schema_based_admin_endpoints_are_available():
    assert ADMIN_SEED_ENABLED, "Test yêu cầu ADMIN_EMAIL và ADMIN_PASSWORD được cấu hình"
    with TestClient(app) as client:
        login = client.post(
            "/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        assert login.status_code == 200, login.text
        token = login.json()["token"]

        for path in [
            "/training-dataset",
            "/model-evaluations",
            "/system-logs",
        ]:
            response = client.get(path, headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200, f"{path} failed: {response.text}"
            assert isinstance(response.json(), list)
