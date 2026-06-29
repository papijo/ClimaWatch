"""Shared test fixtures — in-memory SQLite database with test data."""

import os
os.environ.update({
    "DATABASE_URL": "sqlite:///:memory:",
    "OPENAI_API_KEY": "test",
    "RESEND_API_KEY": "test",
    "JWT_SECRET": "testsecret",
    "MAPBOX_TOKEN": "test",
    "NOAA_TOKEN": "test",
})

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models.state import State
from app.models.risk_assessment import RiskAssessment
from app.models.active_alert import ActiveAlert
from app.models.disease_alert import DiseaseAlert
from app.models.health_facility import HealthFacility
from app.models.lga_vulnerability_score import LGAVulnerabilityScore
from app.models.facility_risk_score import FacilityRiskScore

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@event.listens_for(TEST_ENGINE, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def client(db):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.modules.api.public import router as public_router

    test_app = FastAPI()
    test_app.include_router(public_router)

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = _override_get_db

    with TestClient(test_app) as c:
        yield c


@pytest.fixture()
def seed_state(db):
    state = State(
        id="state-lagos",
        name="Lagos",
        code="LA",
        region="South West",
        capital="Ikeja",
        latitude=6.5227,
        longitude=3.6218,
        current_risk_level="MODERATE",
    )
    db.add(state)
    db.commit()
    return state


@pytest.fixture()
def seed_assessment(db, seed_state):
    assessment = RiskAssessment(
        id="assess-001",
        state_id=seed_state.id,
        risk_level="MODERATE",
        overall_score=45.0,
        climate_score=50.0,
        health_score=40.0,
        vulnerability_score=35.0,
        advisory_en="Monitor conditions.",
        advisory_ha="Kula da yanayi.",
        advisory_yo="Ṣe abojuto ipo naa.",
        advisory_ig="Lezie anya n'ọnọdụ.",
        raw_response={
            "key_drivers": ["rainfall", "temperature"],
            "recommended_actions": ["prepare shelters"],
        },
        assessed_at=datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc),
    )
    db.add(assessment)
    db.commit()
    return assessment


@pytest.fixture()
def seed_active_alert(db, seed_state):
    alert = ActiveAlert(
        id="alert-001",
        state_id=seed_state.id,
        title="HIGH Alert — Lagos",
        description="Flooding risk elevated.",
        risk_level="HIGH",
        is_active=True,
        started_at=datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc),
    )
    db.add(alert)
    db.commit()
    return alert


@pytest.fixture()
def seed_resolved_alert(db, seed_state):
    alert = ActiveAlert(
        id="alert-002",
        state_id=seed_state.id,
        title="Resolved Alert",
        description="Previously elevated.",
        risk_level="HIGH",
        is_active=False,
        started_at=datetime(2026, 6, 25, 10, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 6, 26, 10, 0, tzinfo=timezone.utc),
    )
    db.add(alert)
    db.commit()
    return alert


@pytest.fixture()
def seed_disease_alert(db, seed_state):
    alert = DiseaseAlert(
        id="disease-001",
        state_id=seed_state.id,
        disease_name="Cholera",
        alert_level="warning",
        source="ncdc",
        description="Cases rising in Lagos.",
        is_active=True,
        reported_at=datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc),
    )
    db.add(alert)
    db.commit()
    return alert


@pytest.fixture()
def seed_facility(db, seed_state):
    facility = HealthFacility(
        id="fac-001",
        state_id=seed_state.id,
        lga="Ikeja",
        name="Ikeja General Hospital",
        facility_type="secondary",
        ownership="public",
        category="General Hospital",
        latitude=6.60,
        longitude=3.35,
        source="nhfr",
    )
    db.add(facility)
    db.commit()
    return facility


@pytest.fixture()
def seed_facility_score(db, seed_facility):
    score = FacilityRiskScore(
        id="fscore-001",
        facility_id=seed_facility.id,
        risk_score=62.5,
        flood_risk=70.0,
        heat_stress_risk=55.0,
        disease_burden_risk=60.0,
        infrastructure_vulnerability=65.0,
        scored_at=datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc),
    )
    db.add(score)
    db.commit()
    return score


@pytest.fixture()
def seed_lga_score(db, seed_state):
    score = LGAVulnerabilityScore(
        id="lga-001",
        state_id=seed_state.id,
        lga_name="Ikeja",
        vulnerability_score=55.0,
        population_density_score=70.0,
        health_access_score=45.0,
        climate_exposure_score=50.0,
        scored_at=datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc),
    )
    db.add(score)
    db.commit()
    return score
