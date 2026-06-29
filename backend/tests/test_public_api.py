"""Integration tests for public API endpoints."""

import pytest


class TestListStates:
    def test_returns_all_states(self, client, seed_state):
        resp = client.get("/api/states")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Lagos"
        assert data[0]["current_risk_level"] == "MODERATE"
        assert "password_hash" not in data[0]

    def test_empty_when_no_states(self, client):
        resp = client.get("/api/states")
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetState:
    def test_returns_state_with_assessment(self, client, seed_state, seed_assessment):
        resp = client.get(f"/api/states/{seed_state.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Lagos"
        assert data["latest_assessment"] is not None
        assert data["latest_assessment"]["risk_level"] == "MODERATE"
        assert data["latest_assessment"]["overall_score"] == 45.0

    def test_returns_state_without_assessment(self, client, seed_state):
        resp = client.get(f"/api/states/{seed_state.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latest_assessment"] is None

    def test_404_for_unknown_state(self, client):
        resp = client.get("/api/states/nonexistent")
        assert resp.status_code == 404


class TestGetStateLGAs:
    def test_returns_lga_scores(self, client, seed_lga_score):
        resp = client.get("/api/states/state-lagos/lgas")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["lga_name"] == "Ikeja"
        assert data[0]["vulnerability_score"] == 55.0

    def test_empty_for_state_with_no_lgas(self, client, seed_state):
        resp = client.get(f"/api/states/{seed_state.id}/lgas")
        assert resp.status_code == 200
        assert resp.json() == []


class TestListFacilities:
    def test_returns_facilities_with_score(self, client, seed_facility, seed_facility_score):
        resp = client.get("/api/facilities")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Ikeja General Hospital"
        assert data[0]["latest_risk_score"] is not None
        assert data[0]["latest_risk_score"]["risk_score"] == 62.5

    def test_returns_facility_without_score(self, client, seed_facility):
        resp = client.get("/api/facilities")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["latest_risk_score"] is None

    def test_filter_by_state_id(self, client, seed_facility):
        resp = client.get("/api/facilities?state_id=state-lagos")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = client.get("/api/facilities?state_id=nonexistent")
        assert resp.status_code == 200
        assert resp.json() == []


class TestActiveAlerts:
    def test_returns_active_alerts(self, client, seed_active_alert):
        resp = client.get("/api/alerts/active")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "HIGH Alert — Lagos"
        assert data[0]["is_active"] is True

    def test_excludes_resolved_alerts(self, client, seed_resolved_alert):
        resp = client.get("/api/alerts/active")
        assert resp.status_code == 200
        assert resp.json() == []


class TestAlertHistory:
    def test_returns_resolved_alerts(self, client, seed_resolved_alert):
        resp = client.get("/api/alerts/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["is_active"] is False
        assert data["next_cursor"] is None

    def test_excludes_active_alerts(self, client, seed_active_alert):
        resp = client.get("/api/alerts/history")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 0

    def test_pagination_limit(self, client, seed_resolved_alert):
        resp = client.get("/api/alerts/history?limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 1


class TestDiseaseAlerts:
    def test_returns_active_disease_alerts(self, client, seed_disease_alert):
        resp = client.get("/api/disease-alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["disease_name"] == "Cholera"
        assert data[0]["source"] == "ncdc"

    def test_empty_when_none(self, client):
        resp = client.get("/api/disease-alerts")
        assert resp.status_code == 200
        assert resp.json() == []


class TestForecasts:
    def test_returns_latest_assessment(self, client, seed_assessment):
        resp = client.get("/api/forecasts/state-lagos")
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] == "MODERATE"
        assert data["advisory_en"] == "Monitor conditions."
        assert data["key_drivers"] == ["rainfall", "temperature"]
        assert data["recommended_actions"] == ["prepare shelters"]

    def test_404_for_no_assessment(self, client, seed_state):
        resp = client.get(f"/api/forecasts/{seed_state.id}")
        assert resp.status_code == 404
