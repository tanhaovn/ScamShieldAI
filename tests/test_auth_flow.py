from fastapi.testclient import TestClient

from backend.app.main import app


def test_guest_registration_is_disabled():
    client = TestClient(app)

    register = client.post(
        "/register",
        json={
            "email": "demo.user@example.com",
            "password": "StrongPass123!",
            "full_name": "Demo User",
        },
    )
    assert register.status_code == 403, register.text
    assert "không cần đăng ký" in register.json()["detail"]
