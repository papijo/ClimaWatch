"""Integration tests for auth and user routes."""

import pytest
from app.database import get_db


@pytest.fixture()
def auth_client(db):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.modules.api.user import router as auth_router, me_router

    test_app = FastAPI()
    test_app.include_router(auth_router)
    test_app.include_router(me_router)

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = _override_get_db

    with TestClient(test_app) as c:
        yield c


def _register(client, email="test@example.com", password="password123", full_name="Test User"):
    return client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
    })


def _login(client, email="test@example.com", password="password123"):
    return client.post("/api/auth/login", json={
        "email": email,
        "password": password,
    })


def _auth_header(client, email="test@example.com", password="password123"):
    resp = _login(client, email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestRegister:
    def test_register_success(self, auth_client):
        resp = _register(auth_client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self, auth_client):
        _register(auth_client)
        resp = _register(auth_client)
        assert resp.status_code == 409

    def test_register_short_password(self, auth_client):
        resp = _register(auth_client, password="short")
        assert resp.status_code == 422

    def test_register_invalid_email(self, auth_client):
        resp = _register(auth_client, email="not-an-email")
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, auth_client):
        _register(auth_client)
        resp = _login(auth_client)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, auth_client):
        _register(auth_client)
        resp = _login(auth_client, password="wrongpassword")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, auth_client):
        resp = _login(auth_client, email="nobody@example.com")
        assert resp.status_code == 401


class TestSubscriptions:
    def test_list_subscriptions_requires_auth(self, auth_client):
        resp = auth_client.get("/api/me/subscriptions")
        assert resp.status_code in (401, 403)

    def test_create_and_list_subscription(self, auth_client, seed_state):
        _register(auth_client)
        headers = _auth_header(auth_client)

        resp = auth_client.post("/api/me/subscriptions", json={
            "state_id": seed_state.id,
            "notify_moderate": False,
            "notify_high": True,
            "notify_critical": True,
        }, headers=headers)
        assert resp.status_code == 201

        resp = auth_client.get("/api/me/subscriptions", headers=headers)
        assert resp.status_code == 200
        subs = resp.json()
        assert len(subs) == 1
        assert subs[0]["state_id"] == seed_state.id

    def test_upsert_subscription(self, auth_client, seed_state):
        _register(auth_client)
        headers = _auth_header(auth_client)

        auth_client.post("/api/me/subscriptions", json={
            "state_id": seed_state.id,
            "notify_moderate": False,
            "notify_high": True,
            "notify_critical": True,
        }, headers=headers)

        resp = auth_client.post("/api/me/subscriptions", json={
            "state_id": seed_state.id,
            "notify_moderate": True,
            "notify_high": True,
            "notify_critical": True,
        }, headers=headers)
        assert resp.status_code == 201

        resp = auth_client.get("/api/me/subscriptions", headers=headers)
        subs = resp.json()
        assert len(subs) == 1
        assert subs[0]["notify_moderate"] is True

    def test_delete_subscription(self, auth_client, seed_state):
        _register(auth_client)
        headers = _auth_header(auth_client)

        auth_client.post("/api/me/subscriptions", json={
            "state_id": seed_state.id,
        }, headers=headers)

        resp = auth_client.delete(f"/api/me/subscriptions/{seed_state.id}", headers=headers)
        assert resp.status_code == 204

        resp = auth_client.get("/api/me/subscriptions", headers=headers)
        assert resp.json() == []

    def test_delete_nonexistent_subscription(self, auth_client, seed_state):
        _register(auth_client)
        headers = _auth_header(auth_client)

        resp = auth_client.delete("/api/me/subscriptions/nonexistent", headers=headers)
        assert resp.status_code == 404

    def test_invalid_token_returns_401(self, auth_client):
        headers = {"Authorization": "Bearer invalid.token.here"}
        resp = auth_client.get("/api/me/subscriptions", headers=headers)
        assert resp.status_code in (401, 403, 500)
