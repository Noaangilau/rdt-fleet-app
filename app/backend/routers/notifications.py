"""
notifications.py — In-app notification endpoints.

GET /api/notifications         — list current user's notifications
GET /api/notifications/count   — unread notification count
PUT /api/notifications/{id}/read   — mark a single notification as read
PUT /api/notifications/read-all    — mark all as read
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationOut])
def get_notifications(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all notifications for the current user, newest first."""
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/count", response_model=schemas.NotificationCountOut)
def get_unread_count(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the count of unread notifications for the current user."""
    count = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == current_user.id,
            models.Notification.read == False,
        )
        .count()
    )
    return schemas.NotificationCountOut(count=count)


@router.put("/read-all", response_model=schemas.NotificationCountOut)
def mark_all_read(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all of the current user's notifications as read."""
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.read == False,
    ).update({"read": True})
    db.commit()
    return schemas.NotificationCountOut(count=0)


@router.put("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(
    notification_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single notification as read."""
    notif = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif
