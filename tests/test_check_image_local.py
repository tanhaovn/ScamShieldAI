from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from backend.app.db.database import SessionLocal
from backend.app.db.models import User
from backend.app.main import app, _hash_password


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


def test_default_admin_is_seeded_on_startup():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@scamdetector.local").first()
        if existing:
            db.delete(existing)
            db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        login = client.post(
            "/login",
            json={"email": "admin@scamdetector.local", "password": "Admin@123"},
        )
        assert login.status_code == 200, login.text
        assert login.json()["user"]["role"] == "admin"


def test_schema_based_admin_endpoints_are_available():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@scamdetector.local").first()
        if existing:
            db.delete(existing)
            db.commit()

        admin = User(
            email="admin@scamdetector.local",
            password_hash=_hash_password("Admin@123"),
            full_name="System Admin",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    finally:
        db.close()

    with TestClient(app) as client:
        login = client.post(
            "/login",
            json={"email": "admin@scamdetector.local", "password": "Admin@123"},
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
