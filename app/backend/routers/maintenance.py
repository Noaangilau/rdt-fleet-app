"""
maintenance.py — Maintenance item endpoints.

GET /api/trucks/{id}/maintenance            — all 9 items with computed status
PUT /api/trucks/{id}/maintenance/{item_id}  — record a service performed
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
import models, schemas
from auth import require_manager
from maintenance_logic import calculate_item_status
from models import ITEM_TYPE_LABELS

router = APIRouter(prefix="/api/trucks", tags=["maintenance"])


def _build_item_out(item: models.MaintenanceItem, current_mileage: int) -> schemas.MaintenanceItemOut:
    """Helper: combine DB item fields with computed status fields."""
    computed = calculate_item_status(item, current_mileage)
    return schemas.MaintenanceItemOut(
        id=item.id,
        truck_id=item.truck_id,
        item_type=item.item_type,
        item_label=computed["item_label"],
        last_service_mileage=item.last_service_mileage,
        last_service_date=item.last_service_date,
        interval_miles=item.interval_miles,
        interval_days=item.interval_days,
        notes=item.notes,
        next_due_mileage=computed["next_due_mileage"],
        next_due_date=computed["next_due_date"],
        miles_remaining=computed["miles_remaining"],
        days_remaining=computed["days_remaining"],
        status=computed["status"],
    )


@router.get("/{truck_id}/maintenance", response_model=list[schemas.MaintenanceItemOut])
def get_maintenance_items(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all 9 maintenance items for a truck with their computed statuses."""
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    items = (
        db.query(models.MaintenanceItem)
        .filter(models.MaintenanceItem.truck_id == truck_id)
        .all()
    )
    return [_build_item_out(item, truck.current_mileage) for item in items]


@router.put("/{truck_id}/maintenance/{item_id}", response_model=schemas.MaintenanceItemOut)
def record_service(
    truck_id: int,
    item_id: int,
    data: schemas.RecordServiceRequest,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Record that a maintenance service was performed.
    Updates the last_service_mileage and last_service_date.
    Optionally override the service interval for this specific truck.
    """
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    item = db.query(models.MaintenanceItem).filter(
        models.MaintenanceItem.id == item_id,
        models.MaintenanceItem.truck_id == truck_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Maintenance item not found")

    # Update fields — only set what was provided
    if data.last_service_mileage is not None:
        item.last_service_mileage = data.last_service_mileage
    if data.last_service_date is not None:
        item.last_service_date = data.last_service_date
    if data.notes is not None:
        item.notes = data.notes
    if data.interval_miles is not None:
        item.interval_miles = data.interval_miles
    if data.interval_days is not None:
        item.interval_days = data.interval_days

    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return _build_item_out(item, truck.current_mileage)
