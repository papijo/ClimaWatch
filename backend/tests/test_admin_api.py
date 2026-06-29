"""Integration tests for admin API routes."""

import pytest
from app.database import get_db
from app.models.user import User
from app.models.government_contact import GovernmentContact
from app.modules.auth.password import hash_password
from app.modules.auth.jwt import create_access_token


@pytest.fixture()
def admin_client(db):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.modules.api.admin import router as admin_router

    test_app = FastAPI()
    test_app.include_router(admin_router)

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = _override_get_db

    with TestClient(test_app) as c:
        yield c


@pytest.fixture()
def admin_user(db):
    user = User(
        id="admin-001",
        email="admin@serge.com",
        password_hash=hash_password("adminpass123"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def regular_user(db):
    user = User(
        id="user-001",
        email="user@example.com",
        password_hash=hash_password("userpass123"),
        full_name="Regular User",
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


def _admin_headers(admin_user):
    token = create_access_token(admin_user.id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}


def _user_headers(regular_user):
    token = create_access_token(regular_user.id, regular_user.role)
    return {"Authorization": f"Bearer {token}"}


class TestAdminAuth:
    def test_unauthenticated_returns_401_or_403(self, admin_client):
        resp = admin_client.get("/api/admin/logs")
        assert resp.status_code in (401, 403)

    def test_regular_user_returns_403(self, admin_client, regular_user):
        headers = _user_headers(regular_user)
        resp = admin_client.get("/api/admin/logs", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_access(self, admin_client, admin_user):
        headers = _admin_headers(admin_user)
        resp = admin_client.get("/api/admin/logs", headers=headers)
        assert resp.status_code == 200


class TestAdminLogs:
    def test_returns_logs(self, admin_client, admin_user):
        headers = _admin_headers(admin_user)
        resp = admin_client.get("/api/admin/logs", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestAdminAssessments:
    def test_returns_assessments(self, admin_client, admin_user, seed_assessment):
        headers = _admin_headers(admin_user)
        resp = admin_client.get("/api/admin/assessments", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

    def test_filter_by_state(self, admin_client, admin_user, seed_assessment):
        headers = _admin_headers(admin_user)
        resp = admin_client.get("/api/admin/assessments?state_id=state-lagos", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = admin_client.get("/api/admin/assessments?state_id=nonexistent", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestAdminContacts:
    def _contact_payload(self, state_id="state-lagos"):
        return {
            "state_id": state_id,
            "name": "Dr. Okonkwo",
            "title": "Director of Health",
            "ministry": "Ministry of Health",
            "email": "okonkwo@lagos.gov.ng",
            "phone": "+2348012345678",
        }

    def test_create_contact(self, admin_client, admin_user, seed_state):
        headers = _admin_headers(admin_user)
        resp = admin_client.post("/api/admin/contacts", json=self._contact_payload(), headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Dr. Okonkwo"
        assert "id" in data

    def test_update_contact(self, admin_client, admin_user, seed_state):
        headers = _admin_headers(admin_user)
        resp = admin_client.post("/api/admin/contacts", json=self._contact_payload(), headers=headers)
        contact_id = resp.json()["id"]

        updated = self._contact_payload()
        updated["name"] = "Dr. Adeyemi"
        resp = admin_client.put(f"/api/admin/contacts/{contact_id}", json=updated, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Dr. Adeyemi"

    def test_delete_contact(self, admin_client, admin_user, seed_state):
        headers = _admin_headers(admin_user)
        resp = admin_client.post("/api/admin/contacts", json=self._contact_payload(), headers=headers)
        contact_id = resp.json()["id"]

        resp = admin_client.delete(f"/api/admin/contacts/{contact_id}", headers=headers)
        assert resp.status_code == 204

    def test_delete_nonexistent_contact(self, admin_client, admin_user):
        headers = _admin_headers(admin_user)
        resp = admin_client.delete("/api/admin/contacts/nonexistent", headers=headers)
        assert resp.status_code == 404

    def test_regular_user_cannot_create_contact(self, admin_client, regular_user, seed_state):
        headers = _user_headers(regular_user)
        resp = admin_client.post("/api/admin/contacts", json=self._contact_payload(), headers=headers)
        assert resp.status_code == 403
