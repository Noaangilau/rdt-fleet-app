"""
main.py — RDT Inc. Fleet Management System — FastAPI entry point.

In development: run with `uvicorn main:app --reload --port 8000`
In production:  FastAPI also serves the compiled React build as static files.
                Run with `uvicorn main:app --host 0.0.0.0 --port $PORT`

Startup sequence:
  1. Create all database tables (if they don't exist)
  2. Run seed functions to create the default manager account and demo data
  3. Register all API routers
  4. Mount the React build as static files (production only)
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env file (API keys, JWT secret, database URL)
load_dotenv()

from database import engine, SessionLocal, Base
import models  # noqa — ensures all models are registered with Base before create_all
from seed import run_all_seeds

# Import all routers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from briefing_agent import run_morning_briefing

from routers.auth_router import router as auth_router
from routers.trucks import router as trucks_router
from routers.maintenance import router as maintenance_router
from routers.mileage import router as mileage_router
from routers.incidents import router as incidents_router
from routers.dashboard import router as dashboard_router
from routers.users import router as users_router
from routers.ai import router as ai_router
from routers.operations import router as operations_router
from routers.hr import router as hr_router
from routers.notifications import router as notifications_router
from routers.fleet import router as fleet_router
from routers.briefings import router as briefings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before the app begins serving requests."""
    # Create all database tables from the ORM models
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")

    # Seed default accounts and demo fleet data
    db = SessionLocal()
    try:
        run_all_seeds(db)

        # Start the morning briefing scheduler
        scheduler = AsyncIOScheduler()
        settings = db.query(models.BriefingSettings).first()
        if settings and settings.enabled:
            hour, minute = settings.send_time.split(":")
            scheduler.add_job(
                run_morning_briefing,
                trigger="cron",
                hour=int(hour),
                minute=int(minute),
                id="morning_briefing",
            )
        scheduler.start()
        app.state.scheduler = scheduler
        print("✓ APScheduler started")
    finally:
        db.close()

    yield  # App runs here

    app.state.scheduler.shutdown()


app = FastAPI(
    title="RDT Inc. Fleet Management",
    description="Fleet maintenance tracking for RDT Inc. — Vernal, Utah",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allows the Vite dev server (localhost:5173) to reach this API
# In production, the React build is served by FastAPI directly so CORS is not needed,
# but we keep it here for convenience during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers — all routes are prefixed with /api
app.include_router(auth_router)
app.include_router(trucks_router)
app.include_router(maintenance_router)
app.include_router(mileage_router)
app.include_router(incidents_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(ai_router)
app.include_router(operations_router)
app.include_router(hr_router)
app.include_router(notifications_router)
app.include_router(fleet_router)
app.include_router(briefings_router)


# ---------------------------------------------------------------------------
# Production static file serving
# ---------------------------------------------------------------------------
# In production, the React app is built to app/frontend/dist/.
# FastAPI serves those files so we only need one service on Railway/Render.
# During development, the Vite dev server handles the frontend separately.

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    # Serve React's static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react(full_path: str):
        """
        Catch-all route: serve index.html for any non-API path.
        This enables React Router's client-side routing in production.
        """
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)
