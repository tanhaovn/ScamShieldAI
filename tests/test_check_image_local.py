from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

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
