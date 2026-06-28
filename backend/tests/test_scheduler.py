"""Unit tests for the adaptive scheduler logic."""

from unittest.mock import MagicMock, patch

from apscheduler.triggers.interval import IntervalTrigger

import pytest

from app.modules.scheduler.scheduler import (
    _STATE_JOB_PREFIX,
    _hours_for_level,
    reschedule_state,
    get_scheduler_status,
)


class TestHoursForLevel:
    def test_low_returns_default(self):
        assert _hours_for_level("LOW") == 12

    def test_moderate_returns_elevated(self):
        assert _hours_for_level("MODERATE") == 2

    def test_high_returns_elevated(self):
        assert _hours_for_level("HIGH") == 2

    def test_critical_returns_elevated(self):
        assert _hours_for_level("CRITICAL") == 2


class TestRescheduleState:
    @patch("app.modules.scheduler.scheduler.schedule_state")
    def test_moderate_schedules_elevated(self, mock_schedule):
        reschedule_state("state-001", "MODERATE")
        mock_schedule.assert_called_once_with("state-001", 2)

    @patch("app.modules.scheduler.scheduler.schedule_state")
    def test_high_schedules_elevated(self, mock_schedule):
        reschedule_state("state-001", "HIGH")
        mock_schedule.assert_called_once_with("state-001", 2)

    @patch("app.modules.scheduler.scheduler.schedule_state")
    def test_critical_schedules_elevated(self, mock_schedule):
        reschedule_state("state-001", "CRITICAL")
        mock_schedule.assert_called_once_with("state-001", 2)

    @patch("app.modules.scheduler.scheduler.SessionLocal")
    @patch("app.modules.scheduler.scheduler.should_downgrade_schedule", return_value=True)
    @patch("app.modules.scheduler.scheduler.schedule_state")
    def test_low_with_consecutive_downgrades(self, mock_schedule, mock_should, mock_session):
        reschedule_state("state-001", "LOW")
        mock_schedule.assert_called_once_with("state-001", 12)

    @patch("app.modules.scheduler.scheduler.SessionLocal")
    @patch("app.modules.scheduler.scheduler.should_downgrade_schedule", return_value=False)
    @patch("app.modules.scheduler.scheduler.schedule_state")
    def test_low_without_consecutive_keeps_current(self, mock_schedule, mock_should, mock_session):
        reschedule_state("state-001", "LOW")
        mock_schedule.assert_not_called()


class TestGetSchedulerStatus:
    @patch("app.modules.scheduler.scheduler.scheduler")
    def test_returns_state_jobs_only(self, mock_sched):
        job1 = MagicMock()
        job1.id = f"{_STATE_JOB_PREFIX}state-001"
        job1.next_run_time = MagicMock()
        job1.next_run_time.isoformat.return_value = "2026-06-28T12:00:00+00:00"
        job1.trigger = IntervalTrigger(hours=12)

        job2 = MagicMock()
        job2.id = "some_other_job"

        mock_sched.get_jobs.return_value = [job1, job2]

        result = get_scheduler_status()
        assert len(result) == 1
        assert result[0]["state_id"] == "state-001"
        assert result[0]["interval_hours"] == 12
        assert result[0]["next_run"] == "2026-06-28T12:00:00+00:00"

    @patch("app.modules.scheduler.scheduler.scheduler")
    def test_empty_when_no_jobs(self, mock_sched):
        mock_sched.get_jobs.return_value = []
        assert get_scheduler_status() == []
