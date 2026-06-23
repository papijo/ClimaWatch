import logging

from sqlalchemy.orm import Session

from app.models.state import State
from app.modules.data_pipeline import open_meteo, nasa_power, noaa_cdo

logger = logging.getLogger(__name__)


async def run_pipeline_for_state(state: State, db: Session) -> int:
    """Fetches climate data from all sources for a single state. Returns count of readings stored."""
    stored = 0

    om = await open_meteo.fetch_and_store(state.id, state.latitude, state.longitude, db)
    if om:
        stored += 1

    np = await nasa_power.fetch_and_store(state.id, state.latitude, state.longitude, db)
    if np:
        stored += 1

    nc = await noaa_cdo.fetch_and_store(state.id, state.code, db)
    if nc:
        stored += 1

    if stored > 0:
        db.commit()
        logger.info("State %s: stored %d climate readings", state.name, stored)
    else:
        logger.warning("State %s: no climate data collected from any source", state.name)

    return stored


async def run_pipeline_all(db: Session) -> dict[str, int]:
    """Runs the pipeline for all states. Returns {state_name: readings_stored}."""
    states = db.query(State).order_by(State.name).all()
    results = {}
    for state in states:
        count = await run_pipeline_for_state(state, db)
        results[state.name] = count
    return results
