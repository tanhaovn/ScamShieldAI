from fastapi.testclient import TestClient

from backend.app.main import app


def test_register_login_and_me():
    client = TestClient(app)

    register = client.post(
        "/register",
        json={
            "email": "demo.user@example.com",
            "password": "StrongPass123!",
            "full_name": "Demo User",
        },
    )
    assert register.status_code == 200, register.text
    register_payload = register.json()
    assert register_payload["user"]["email"] == "demo.user@example.com"
    assert "token" in register_payload

    login = client.post(
        "/login",
        json={
            "email": "demo.user@example.com",
            "password": "StrongPass123!",
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["token"]
    assert token

    me = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "demo.user@example.com"
