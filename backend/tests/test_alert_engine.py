"""Unit tests for the alert engine: handler, website alerts, email dispatch, subscribers."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

import pytest


def _make_state(name: str = "Lagos", state_id: str = "state-001") -> MagicMock:
    state = MagicMock()
    state.id = state_id
    state.name = name
    state.current_risk_level = "LOW"
    return state


def _make_db() -> MagicMock:
    return MagicMock()


def _make_assessment(advisory: str = "Stay safe.") -> MagicMock:
    a = MagicMock()
    a.advisory_en = advisory
    a.state_id = "state-001"
    return a


class TestOnRiskTransition:
    @patch("app.modules.alert_engine.handler.dispatch_alerts")
    @patch("app.modules.alert_engine.handler.get_subscribers")
    @patch("app.modules.alert_engine.handler.create_alert")
    def test_high_creates_alert_and_dispatches(self, mock_create, mock_subs, mock_dispatch):
        from app.modules.alert_engine.handler import on_risk_transition

        db = _make_db()
        state = _make_state()
        assessment = _make_assessment()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = assessment
        mock_subs.return_value = [{"email": "a@b.com", "full_name": "Test", "user_id": "u1"}]
        mock_dispatch.return_value = {"sent": 1, "failed": 0}

        on_risk_transition(db, state, "MODERATE", "HIGH")

        mock_create.assert_called_once()
        mock_subs.assert_called_once_with(db, "state-001", "HIGH")
        mock_dispatch.assert_called_once()

    @patch("app.modules.alert_engine.handler.dispatch_alerts")
    @patch("app.modules.alert_engine.handler.get_subscribers")
    @patch("app.modules.alert_engine.handler.create_alert")
    def test_critical_creates_alert(self, mock_create, mock_subs, mock_dispatch):
        from app.modules.alert_engine.handler import on_risk_transition

        db = _make_db()
        state = _make_state()
        assessment = _make_assessment()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = assessment
        mock_subs.return_value = []

        on_risk_transition(db, state, "HIGH", "CRITICAL")

        mock_create.assert_called_once()
        mock_dispatch.assert_not_called()

    @patch("app.modules.alert_engine.handler.resolve_alerts")
    @patch("app.modules.alert_engine.handler.create_alert")
    def test_high_to_low_resolves_alerts(self, mock_create, mock_resolve):
        from app.modules.alert_engine.handler import on_risk_transition

        db = _make_db()
        state = _make_state()
        mock_resolve.return_value = 2

        on_risk_transition(db, state, "HIGH", "LOW")

        mock_create.assert_not_called()
        mock_resolve.assert_called_once_with(db, "state-001")

    @patch("app.modules.alert_engine.handler.resolve_alerts")
    @patch("app.modules.alert_engine.handler.create_alert")
    def test_low_to_moderate_no_action(self, mock_create, mock_resolve):
        from app.modules.alert_engine.handler import on_risk_transition

        db = _make_db()
        state = _make_state()

        on_risk_transition(db, state, "LOW", "MODERATE")

        mock_create.assert_not_called()
        mock_resolve.assert_not_called()


class TestWebsiteAlerts:
    def test_create_alert(self):
        from app.modules.alert_engine.website_alerts import create_alert

        db = _make_db()
        state = _make_state()

        alert = create_alert(db, state, "Test Alert", "Description", "HIGH")
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_resolve_alerts(self):
        from app.modules.alert_engine.website_alerts import resolve_alerts

        db = _make_db()
        alert1 = MagicMock(is_active=True, ended_at=None)
        alert2 = MagicMock(is_active=True, ended_at=None)
        db.query.return_value.filter.return_value.all.return_value = [alert1, alert2]

        count = resolve_alerts(db, "state-001")
        assert count == 2
        assert alert1.is_active is False
        assert alert2.is_active is False
        db.commit.assert_called_once()

    def test_resolve_no_active_alerts(self):
        from app.modules.alert_engine.website_alerts import resolve_alerts

        db = _make_db()
        db.query.return_value.filter.return_value.all.return_value = []

        count = resolve_alerts(db, "state-001")
        assert count == 0

    def test_create_disease_website_alert_warning(self):
        from app.modules.alert_engine.website_alerts import create_disease_website_alert

        db = _make_db()
        state = _make_state()
        db.query.return_value.filter.return_value.first.return_value = state

        disease_alert = MagicMock()
        disease_alert.alert_level = "warning"
        disease_alert.state_id = "state-001"
        disease_alert.disease_name = "Cholera"
        disease_alert.description = "Outbreak in progress"

        result = create_disease_website_alert(db, disease_alert)
        assert result is not None
        assert db.add.call_count >= 1

    def test_create_disease_website_alert_watch_skipped(self):
        from app.modules.alert_engine.website_alerts import create_disease_website_alert

        db = _make_db()
        disease_alert = MagicMock()
        disease_alert.alert_level = "watch"
        disease_alert.state_id = "state-001"

        result = create_disease_website_alert(db, disease_alert)
        assert result is None

    def test_create_disease_website_alert_no_state_skipped(self):
        from app.modules.alert_engine.website_alerts import create_disease_website_alert

        db = _make_db()
        disease_alert = MagicMock()
        disease_alert.alert_level = "emergency"
        disease_alert.state_id = None

        result = create_disease_website_alert(db, disease_alert)
        assert result is None


class TestEmailDispatch:
    def test_build_alert_html_contains_key_elements(self):
        from app.modules.alert_engine.email_dispatch import build_alert_html

        html = build_alert_html("Lagos", "CRITICAL", "Evacuate low areas.", "Jonathan")
        assert "Lagos" in html
        assert "CRITICAL" in html
        assert "Evacuate low areas." in html
        assert "Jonathan" in html
        assert "climawatch.ng" in html

    @patch("app.modules.alert_engine.email_dispatch.resend")
    def test_dispatch_alerts_counts(self, mock_resend):
        from app.modules.alert_engine.email_dispatch import dispatch_alerts

        mock_resend.Emails.send.return_value = {"id": "msg-123"}

        subscribers = [
            {"email": "a@b.com", "full_name": "Alice", "user_id": "u1"},
            {"email": "c@d.com", "full_name": "Bob", "user_id": "u2"},
        ]
        result = dispatch_alerts(subscribers, "Lagos", "HIGH", "Stay safe.")
        assert result == {"sent": 2, "failed": 0}
        assert mock_resend.Emails.send.call_count == 2

    @patch("app.modules.alert_engine.email_dispatch.resend")
    def test_dispatch_alerts_handles_failure(self, mock_resend):
        from app.modules.alert_engine.email_dispatch import dispatch_alerts

        mock_resend.Emails.send.side_effect = Exception("API error")

        subscribers = [{"email": "a@b.com", "full_name": "Alice", "user_id": "u1"}]
        result = dispatch_alerts(subscribers, "Lagos", "HIGH", "Stay safe.")
        assert result == {"sent": 0, "failed": 1}


class TestSubscribers:
    def test_get_subscribers_for_high(self):
        from app.modules.alert_engine.subscribers import get_subscribers

        db = _make_db()
        db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            ("a@b.com", "Alice", "u1"),
            ("c@d.com", "Bob", "u2"),
        ]

        result = get_subscribers(db, "state-001", "HIGH")
        assert len(result) == 2
        assert result[0]["email"] == "a@b.com"
        assert result[1]["full_name"] == "Bob"

    def test_get_subscribers_low_returns_empty(self):
        from app.modules.alert_engine.subscribers import get_subscribers

        db = _make_db()
        result = get_subscribers(db, "state-001", "LOW")
        assert result == []

    def test_get_subscribers_empty_list(self):
        from app.modules.alert_engine.subscribers import get_subscribers

        db = _make_db()
        db.query.return_value.join.return_value.filter.return_value.all.return_value = []

        result = get_subscribers(db, "state-001", "CRITICAL")
        assert result == []
