from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.api.public import router as public_router
from app.modules.api.user import router as auth_router, me_router
from app.modules.api.admin import router as admin_router
from app.modules.scheduler.scheduler import start as start_scheduler, stop as stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


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
