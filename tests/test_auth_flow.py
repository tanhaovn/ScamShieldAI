import uuid

from fastapi.testclient import TestClient

from backend.app.main import app


def test_user_can_register_login_and_is_blocked_from_admin_login():
    client = TestClient(app)

    email = f"demo-{uuid.uuid4().hex}@example.com"

    register = client.post(
        "/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Demo User",
        },
    )
    assert register.status_code == 201, register.text
    assert register.json()["user"]["role"] == "user"

    login = client.post(
        "/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["token"]

    admin_login = client.post(
        "/admin/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert admin_login.status_code == 403, admin_login.text
