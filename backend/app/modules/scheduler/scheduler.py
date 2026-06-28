import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import SessionLocal
from app.models.state import State
from app.modules.risk_manager.manager import should_downgrade_schedule

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

_STATE_JOB_PREFIX = "assess_state_"


def start():
    if not scheduler.running:
        scheduler.start()


def stop():
    if scheduler.running:
        scheduler.shutdown(wait=False)


def _hours_for_level(risk_level: str) -> int:
    if risk_level in ("MODERATE", "HIGH", "CRITICAL"):
        return settings.ELEVATED_CYCLE_HOURS
    return settings.DEFAULT_CYCLE_HOURS


def register_all_states() -> int:
    """Load all states from DB and register a recurring assessment job for each."""
    db = SessionLocal()
    try:
        states = db.query(State).all()
        for state in states:
            hours = _hours_for_level(state.current_risk_level)
            schedule_state(state.id, hours)
        logger.info("Registered %d state assessment jobs", len(states))
        return len(states)
    finally:
        db.close()


def schedule_state(state_id: str, hours: int) -> None:
    job_id = f"{_STATE_JOB_PREFIX}{state_id}"
    if scheduler.get_job(job_id):
        scheduler.reschedule_job(job_id, trigger=IntervalTrigger(hours=hours))
        logger.debug("Rescheduled %s to every %dh", job_id, hours)
    else:
        scheduler.add_job(
            run_state_assessment,
            trigger=IntervalTrigger(hours=hours),
            id=job_id,
            args=[state_id],
            replace_existing=True,
        )
        logger.debug("Registered %s at every %dh", job_id, hours)


def reschedule_state(state_id: str, new_risk_level: str) -> None:
    """Reschedule a state's job based on its new risk level.

    If the new level is LOW, only downgrade to 12h if the state has had
    2 consecutive LOW assessments (checked via should_downgrade_schedule).
    """
    if new_risk_level in ("MODERATE", "HIGH", "CRITICAL"):
        schedule_state(state_id, settings.ELEVATED_CYCLE_HOURS)
    else:
        db = SessionLocal()
        try:
            if should_downgrade_schedule(db, state_id):
                schedule_state(state_id, settings.DEFAULT_CYCLE_HOURS)
        finally:
            db.close()


async def run_state_assessment(state_id: str) -> None:
    """Full assessment pipeline for a single state:
    data pipeline -> AI engine -> risk manager -> reschedule.
    """
    from app.modules.data_pipeline.runner import run_pipeline_for_state
    from app.modules.ai_engine.service import run_assessment

    db = SessionLocal()
    try:
        state = db.query(State).filter(State.id == state_id).first()
        if not state:
            logger.error("State %s not found, skipping assessment", state_id)
            return

        logger.info("Starting assessment pipeline for %s", state.name)

        await run_pipeline_for_state(state, db)

        assessment = await run_assessment(state_id, db)

        reschedule_state(state_id, assessment.risk_level)

        logger.info(
            "Assessment pipeline complete for %s: %s (score=%.1f)",
            state.name, assessment.risk_level, assessment.overall_score,
        )
    except Exception:
        logger.exception("Assessment pipeline failed for state %s", state_id)
    finally:
        db.close()


def get_scheduler_status() -> list[dict]:
    """Return status of all registered state assessment jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        if not job.id.startswith(_STATE_JOB_PREFIX):
            continue
        state_id = job.id[len(_STATE_JOB_PREFIX):]
        trigger = job.trigger
        interval_hours = None
        if isinstance(trigger, IntervalTrigger):
            interval_hours = int(trigger.interval.total_seconds() / 3600)
        jobs.append({
            "state_id": state_id,
            "job_id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "interval_hours": interval_hours,
        })
    return jobs
