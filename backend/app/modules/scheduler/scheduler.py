from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

scheduler = AsyncIOScheduler()

_STATE_JOB_PREFIX = "assess_state_"


def start():
    if not scheduler.running:
        scheduler.start()


def stop():
    if scheduler.running:
        scheduler.shutdown(wait=False)


def schedule_state(state_id: str, hours: int, func) -> None:
    job_id = f"{_STATE_JOB_PREFIX}{state_id}"
    if scheduler.get_job(job_id):
        scheduler.reschedule_job(job_id, trigger=IntervalTrigger(hours=hours))
    else:
        scheduler.add_job(
            func,
            trigger=IntervalTrigger(hours=hours),
            id=job_id,
            args=[state_id],
            replace_existing=True,
        )


def reschedule_state(state_id: str, risk_level: str, func) -> None:
    hours = (
        settings.ELEVATED_CYCLE_HOURS
        if risk_level in ("MODERATE", "HIGH", "CRITICAL")
        else settings.DEFAULT_CYCLE_HOURS
    )
    schedule_state(state_id, hours, func)
