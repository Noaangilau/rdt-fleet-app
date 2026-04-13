"""
routers/briefings.py — Morning Ops Briefing configuration and history endpoints.

All endpoints require manager role.

GET  /api/briefings/settings  — return current settings (creates defaults if missing)
PUT  /api/briefings/settings  — update and reschedule the APScheduler job
GET  /api/briefings/history   — last 7 briefing log entries, newest first
POST /api/briefings/send-now  — trigger a briefing immediately (for testing)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from auth import require_manager
import models
import schemas
from briefing_agent import run_morning_briefing

router = APIRouter(prefix="/api/briefings", tags=["briefings"])

JOB_ID = "morning_briefing"


def _get_or_create_settings(db: Session) -> models.BriefingSettings:
    """Return the single BriefingSettings row, creating it with defaults if missing."""
    settings = db.query(models.BriefingSettings).first()
    if not settings:
        settings = models.BriefingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _reschedule(request: Request, settings: models.BriefingSettings):
    """
    Reschedule (or remove) the APScheduler job based on current settings.
    Safe to call even if the scheduler isn't initialised (e.g. in tests).
    """
    try:
        scheduler = request.app.state.scheduler
    except AttributeError:
        return

    if scheduler.get_job(JOB_ID):
        scheduler.remove_job(JOB_ID)

    if settings.enabled:
        hour, minute = settings.send_time.split(":")
        scheduler.add_job(
            run_morning_briefing,
            trigger="cron",
            hour=int(hour),
            minute=int(minute),
            id=JOB_ID,
            replace_existing=True,
        )


@router.get("/settings", response_model=schemas.BriefingSettingsOut)
def get_settings(
    _: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return the current briefing configuration."""
    return _get_or_create_settings(db)


@router.put("/settings", response_model=schemas.BriefingSettingsOut)
def update_settings(
    body: schemas.BriefingSettingsUpdate,
    request: Request,
    _: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update briefing settings and reschedule the daily job."""
    settings = _get_or_create_settings(db)
    settings.enabled = body.enabled
    settings.send_time = body.send_time
    settings.email_address = body.email_address
    db.commit()
    db.refresh(settings)
    _reschedule(request, settings)
    return settings


@router.get("/history", response_model=list[schemas.BriefingLogOut])
def get_history(
    _: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return the last 7 briefing log entries, newest first."""
    return (
        db.query(models.BriefingLog)
        .order_by(models.BriefingLog.sent_at.desc())
        .limit(7)
        .all()
    )


@router.post("/send-now", response_model=schemas.BriefingLogOut)
def send_now(
    _: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Trigger the morning briefing immediately (for testing/manual sends).
    Runs synchronously — FastAPI executes sync endpoints in a thread pool.
    Returns the log entry that was just created.
    """
    run_morning_briefing()

    log = (
        db.query(models.BriefingLog)
        .order_by(models.BriefingLog.sent_at.desc())
        .first()
    )
    if not log:
        raise HTTPException(status_code=500, detail="Briefing ran but no log entry was found")
    return log
