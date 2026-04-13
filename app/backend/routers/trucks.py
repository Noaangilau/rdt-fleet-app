"""
trucks.py — CRUD endpoints for fleet trucks.

GET    /api/trucks           — list all trucks
POST   /api/trucks           — add a truck (auto-creates 9 maintenance rows)
GET    /api/trucks/summary   — lightweight list for driver dropdowns
GET    /api/trucks/{id}      — single truck with full maintenance status
PUT    /api/trucks/{id}      — update truck info
DELETE /api/trucks/{id}      — remove truck (cascades maintenance + incidents)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from models import MAINTENANCE_ITEM_TYPES, DEFAULT_INTERVALS
from auth import require_manager, require_driver
from maintenance_logic import calculate_item_status, get_truck_overall_status
from models import ITEM_TYPE_LABELS

router = APIRouter(prefix="/api/trucks", tags=["trucks"])


@router.get("/summary", response_model=list[schemas.TruckSummary])
def get_trucks_summary(
    current_user: models.User = Depends(require_driver),
    db: Session = Depends(get_db),
):
    """Return a lightweight truck list for driver mileage/incident dropdowns."""
    return db.query(models.Truck).order_by(models.Truck.truck_number).all()


@router.get("", response_model=list[schemas.TruckOut])
def get_trucks(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all trucks, ordered by truck number."""
    return db.query(models.Truck).order_by(models.Truck.truck_number).all()


@router.post("", response_model=schemas.TruckOut, status_code=status.HTTP_201_CREATED)
def create_truck(
    data: schemas.TruckCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Add a new truck to the fleet.
    Automatically creates all 9 maintenance item rows with default intervals.
    """
    # Check for duplicate truck number
    if db.query(models.Truck).filter(models.Truck.truck_number == data.truck_number).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Truck number '{data.truck_number}' already exists",
        )

    truck = models.Truck(**data.model_dump())
    db.add(truck)
    db.flush()  # get truck.id before creating maintenance items

    # Auto-create all 9 maintenance item rows for this truck
    for item_type in MAINTENANCE_ITEM_TYPES:
        defaults = DEFAULT_INTERVALS[item_type]
        item = models.MaintenanceItem(
            truck_id=truck.id,
            item_type=item_type,
            interval_miles=defaults["miles"],
            interval_days=defaults["days"],
        )
        db.add(item)

    db.commit()
    db.refresh(truck)
    return truck


@router.get("/{truck_id}", response_model=schemas.TruckOut)
def get_truck(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return a single truck by ID."""
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.put("/{truck_id}", response_model=schemas.TruckOut)
def update_truck(
    truck_id: int,
    data: schemas.TruckUpdate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update truck metadata. Only provided fields are changed."""
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(truck, field, value)

    db.commit()
    db.refresh(truck)
    return truck


@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truck(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Remove a truck from the fleet.
    Cascades to delete all maintenance items, incidents, and mileage logs.
    """
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    db.delete(truck)
    db.commit()
