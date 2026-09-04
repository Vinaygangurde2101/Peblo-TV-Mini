from app.auth.jwt import create_access_token
from app.models.user import UserRole


def test_login_success(client, admin_user):
    response = client.post(
        "/auth/login",
        json={"email": "test_admin@peblo.tv", "password": "admin_pass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "test_admin@peblo.tv"


def test_login_invalid_password(client, admin_user):
    response = client.post(
        "/auth/login",
        json={"email": "test_admin@peblo.tv", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_get_current_user_profile(client, editor_user):
    token = create_access_token(user_id=editor_user.id, email=editor_user.email, role=editor_user.role)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_editor@peblo.tv"
    assert data["role"] == "editor"


def test_unauthenticated_access_denied(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
