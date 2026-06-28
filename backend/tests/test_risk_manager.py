"""Unit tests for risk manager transition logic."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.modules.risk_manager.manager import (
    apply_risk_transition,
    build_transition_reason,
    get_consecutive_low_count,
    register_transition_callback,
    should_downgrade_schedule,
    _on_transition_callbacks,
)


def _make_state(current_level: str = "LOW") -> MagicMock:
    state = MagicMock()
    state.id = "state-001"
    state.name = "Lagos"
    state.current_risk_level = current_level
    return state


def _make_db() -> MagicMock:
    return MagicMock()


def _make_assessment(score: float = 55.0, climate: float = 60.0,
                     health: float = 50.0, vuln: float = 45.0) -> MagicMock:
    assessment = MagicMock()
    assessment.overall_score = score
    assessment.climate_score = climate
    assessment.health_score = health
    assessment.vulnerability_score = vuln
    return assessment


class TestApplyRiskTransition:
    def setup_method(self):
        _on_transition_callbacks.clear()

    def test_no_change_returns_false(self):
        db = _make_db()
        state = _make_state("LOW")
        assert apply_risk_transition(db, state, "LOW") is False
        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_low_to_moderate(self):
        db = _make_db()
        state = _make_state("LOW")
        result = apply_risk_transition(db, state, "MODERATE", reason="test")
        assert result is True
        assert state.current_risk_level == "MODERATE"
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_moderate_to_high(self):
        db = _make_db()
        state = _make_state("MODERATE")
        result = apply_risk_transition(db, state, "HIGH")
        assert result is True
        assert state.current_risk_level == "HIGH"

    def test_high_to_critical(self):
        db = _make_db()
        state = _make_state("HIGH")
        result = apply_risk_transition(db, state, "CRITICAL")
        assert result is True
        assert state.current_risk_level == "CRITICAL"

    def test_high_to_low(self):
        db = _make_db()
        state = _make_state("HIGH")
        result = apply_risk_transition(db, state, "LOW")
        assert result is True
        assert state.current_risk_level == "LOW"

    def test_risk_state_change_record_created(self):
        db = _make_db()
        state = _make_state("MODERATE")
        apply_risk_transition(db, state, "HIGH", reason="scores elevated")
        added_obj = db.add.call_args[0][0]
        assert added_obj.state_id == "state-001"
        assert added_obj.from_level == "MODERATE"
        assert added_obj.to_level == "HIGH"
        assert added_obj.reason == "scores elevated"

    def test_callback_fires_on_transition(self):
        callback = MagicMock()
        register_transition_callback(callback)
        db = _make_db()
        state = _make_state("LOW")
        apply_risk_transition(db, state, "HIGH")
        callback.assert_called_once_with(db, state, "LOW", "HIGH")

    def test_callback_not_fired_when_no_change(self):
        callback = MagicMock()
        register_transition_callback(callback)
        db = _make_db()
        state = _make_state("LOW")
        apply_risk_transition(db, state, "LOW")
        callback.assert_not_called()

    def test_callback_exception_does_not_break_transition(self):
        callback = MagicMock(side_effect=RuntimeError("callback failed"))
        register_transition_callback(callback)
        db = _make_db()
        state = _make_state("LOW")
        result = apply_risk_transition(db, state, "MODERATE")
        assert result is True
        assert state.current_risk_level == "MODERATE"


class TestGetConsecutiveLowCount:
    def _setup_query(self, db, levels: list[str]):
        rows = [(level,) for level in levels]
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = rows

    def test_all_low(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "LOW", "LOW"])
        assert get_consecutive_low_count(db, "state-001") == 3

    def test_none_low(self):
        db = _make_db()
        self._setup_query(db, ["MODERATE", "HIGH", "CRITICAL"])
        assert get_consecutive_low_count(db, "state-001") == 0

    def test_mixed_recent_low(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "LOW", "MODERATE"])
        assert get_consecutive_low_count(db, "state-001") == 2

    def test_low_then_high_then_low(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "HIGH", "LOW"])
        assert get_consecutive_low_count(db, "state-001") == 1

    def test_no_assessments(self):
        db = _make_db()
        self._setup_query(db, [])
        assert get_consecutive_low_count(db, "state-001") == 0


class TestShouldDowngradeSchedule:
    def _setup_query(self, db, levels: list[str]):
        rows = [(level,) for level in levels]
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = rows

    def test_two_consecutive_low_returns_true(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "LOW"])
        assert should_downgrade_schedule(db, "state-001") is True

    def test_three_consecutive_low_returns_true(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "LOW", "LOW"])
        assert should_downgrade_schedule(db, "state-001") is True

    def test_one_low_returns_false(self):
        db = _make_db()
        self._setup_query(db, ["LOW", "MODERATE"])
        assert should_downgrade_schedule(db, "state-001") is False

    def test_no_assessments_returns_false(self):
        db = _make_db()
        self._setup_query(db, [])
        assert should_downgrade_schedule(db, "state-001") is False


class TestBuildTransitionReason:
    def test_format(self):
        assessment = _make_assessment(55.0, 60.0, 50.0, 45.0)
        reason = build_transition_reason(assessment)
        assert "55.0/100" in reason
        assert "climate=60.0" in reason
        assert "health=50.0" in reason
        assert "vulnerability=45.0" in reason
