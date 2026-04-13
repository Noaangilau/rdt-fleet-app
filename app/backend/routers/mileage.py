"""
mileage.py — Driver mileage submission endpoint.

POST /api/mileage — update a truck's current mileage and log the entry
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
import models, schemas
from auth import require_driver

router = APIRouter(prefix="/api/mileage", tags=["mileage"])


@router.post("", response_model=schemas.MileageLogOut, status_code=status.HTTP_201_CREATED)
def submit_mileage(
    data: schemas.MileageSubmit,
    current_user: models.User = Depends(require_driver),
    db: Session = Depends(get_db),
):
    """
    Driver submits the current odometer reading for their truck.
    Updates the truck's current_mileage and logs the entry for audit purposes.
    Rejects a mileage that is lower than the truck's current recorded mileage.
    """
    truck = db.query(models.Truck).filter(models.Truck.id == data.truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    # Sanity check — odometer should never go backward
    if data.mileage < truck.current_mileage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Submitted mileage ({data.mileage:,}) is less than the truck's "
                f"current recorded mileage ({truck.current_mileage:,}). "
                "Please check the odometer and try again."
            ),
        )

    # Update the truck's mileage
    truck.current_mileage = data.mileage
    truck.updated_at = datetime.now(timezone.utc)

    # Log this submission for the audit trail
    log = models.MileageLog(
        truck_id=truck.id,
        reported_mileage=data.mileage,
        reported_by=current_user.username,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
