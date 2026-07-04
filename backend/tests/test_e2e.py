"""
End-to-end smoke test for the full assessment pipeline.

Requires:
  E2E=1                     — opt-in env var to activate
  TEST_DATABASE_URL         — PostgreSQL URL seeded with states
  OPENAI_API_KEY            — real key (not "test")

Run with:
  E2E=1 TEST_DATABASE_URL=postgresql://... pytest tests/test_e2e.py -v
"""

import asyncio
import os

import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module", autouse=True)
def require_e2e_env():
    if not os.environ.get("E2E"):
        pytest.skip("Set E2E=1 to run end-to-end tests")


def test_full_pipeline_lagos():
    """
    Run the complete assessment pipeline for Lagos and assert that every
    downstream DB row is created: RiskAssessment, RiskStateChange (if level
    changes), and ActiveAlert (if the resulting level is HIGH or CRITICAL).
    """
    from app.database import SessionLocal
    from app.models.state import State
    from app.models.risk_assessment import RiskAssessment
    from app.models.risk_state_change import RiskStateChange
    from app.modules.scheduler.scheduler import run_state_assessment

    db = SessionLocal()
    try:
        state = db.query(State).filter_by(name="Lagos").first()
        assert state is not None, (
            "Lagos not found — run seed_states.py before the E2E suite"
        )
        state_id = state.id
        initial_level = state.current_risk_level

        # Run the full pipeline synchronously
        asyncio.run(run_state_assessment(state_id))

        db.expire_all()

        # 1. RiskAssessment row must exist
        assessment = (
            db.query(RiskAssessment)
            .filter_by(state_id=state_id)
            .order_by(RiskAssessment.assessed_at.desc())
            .first()
        )
        assert assessment is not None, "No RiskAssessment created for Lagos"
        assert assessment.risk_level in ("LOW", "MODERATE", "HIGH", "CRITICAL")
        assert 0.0 <= assessment.overall_score <= 100.0
        assert assessment.advisory_en
        assert assessment.advisory_ha
        assert assessment.advisory_yo
        assert assessment.advisory_ig

        # 2. State's current_risk_level must be updated
        db.refresh(state)
        assert state.current_risk_level == assessment.risk_level

        # 3. If the risk level changed, a RiskStateChange row must exist
        if state.current_risk_level != initial_level:
            change = (
                db.query(RiskStateChange)
                .filter_by(state_id=state_id)
                .order_by(RiskStateChange.changed_at.desc())
                .first()
            )
            assert change is not None, "Level changed but no RiskStateChange row created"
            assert change.to_level == assessment.risk_level
            assert change.from_level == initial_level

        # 4. If HIGH or CRITICAL, an active alert must exist
        if assessment.risk_level in ("HIGH", "CRITICAL"):
            from app.models.active_alert import ActiveAlert
            alert = (
                db.query(ActiveAlert)
                .filter_by(state_id=state_id, is_active=True)
                .first()
            )
            assert alert is not None, (
                f"Expected an active alert for {assessment.risk_level} risk in Lagos"
            )

    finally:
        db.close()
