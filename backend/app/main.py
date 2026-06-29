import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.api.public import router as public_router
from app.modules.api.user import router as auth_router, me_router
from app.modules.api.admin import router as admin_router
from app.modules.alert_engine.handler import on_risk_transition
from app.modules.risk_manager.manager import register_transition_callback
from app.modules.scheduler.scheduler import (
    start as start_scheduler,
    stop as stop_scheduler,
    register_all_states,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_transition_callback(on_risk_transition)
    start_scheduler()
    count = register_all_states()
    logger.info("Scheduler started with %d state jobs", count)
    yield
    stop_scheduler()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="ClimaWatch API",
    description="AI-powered climate-health intelligence platform for Nigeria",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"status": "ok"}
