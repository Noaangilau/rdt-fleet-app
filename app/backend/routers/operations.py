"""
operations.py — Operations & dispatch endpoints.

GET  /api/operations/availability              — all driver availability statuses
PUT  /api/operations/availability              — driver updates own status
GET  /api/operations/routes                    — list all routes
POST /api/operations/routes                    — create a route
PUT  /api/operations/routes/{id}               — update a route
DELETE /api/operations/routes/{id}             — delete a route
GET  /api/operations/missed-pickups            — list missed pickups
POST /api/operations/missed-pickups            — report a missed pickup
PUT  /api/operations/missed-pickups/{id}/approve — manager approves
GET  /api/operations/approvals                 — list approval queue
PUT  /api/operations/approvals/{id}            — manager approves/rejects an item
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
from database import get_db
import models
import schemas
from auth import require_manager, get_current_user

router = APIRouter(prefix="/api/operations", tags=["operations"])


# ---------------------------------------------------------------------------
# Driver Availability
# ---------------------------------------------------------------------------

@router.get("/availability", response_model=list[schemas.AvailabilityOut])
def get_availability(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return availability status for all drivers."""
    drivers = db.query(models.User).filter(models.User.role == "driver").all()
    results = []
    for driver in drivers:
        avail = db.query(models.DriverAvailability).filter(
            models.DriverAvailability.driver_id == driver.id
        ).first()

        results.append(schemas.AvailabilityOut(
            id=avail.id if avail else 0,
            driver_id=driver.id,
            driver_name=driver.full_name,
            username=driver.username,
            status=avail.status if avail else "off_duty",
            current_route=avail.current_route if avail else None,
            last_updated=avail.last_updated if avail else None,
        ))
    return results


@router.put("/availability", response_model=schemas.AvailabilityOut)
def update_availability(
    data: schemas.AvailabilityUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Driver or manager updates a driver's availability status."""
    valid_statuses = ("on_duty", "available", "off_duty")
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    # Drivers can only update their own status; managers can update any driver
    target_id = data.user_id if (current_user.role == "manager" and data.user_id) else current_user.id

    avail = db.query(models.DriverAvailability).filter(
        models.DriverAvailability.driver_id == target_id
    ).first()

    if not avail:
        avail = models.DriverAvailability(
            driver_id=target_id,
            status=data.status,
            current_route=data.current_route,
        )
        db.add(avail)
    else:
        avail.status = data.status
        if data.current_route is not None:
            avail.current_route = data.current_route
        avail.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(avail)

    user = db.query(models.User).filter(models.User.id == target_id).first()
    return schemas.AvailabilityOut(
        id=avail.id,
        driver_id=user.id,
        driver_name=user.full_name,
        username=user.username,
        status=avail.status,
        current_route=avail.current_route,
        last_updated=avail.last_updated,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/routes", response_model=list[schemas.RouteOut])
def get_routes(
    route_date: date = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all routes, optionally filtered by date."""
    query = db.query(models.Route)
    if route_date:
        query = query.filter(models.Route.date == route_date)
    return query.order_by(models.Route.date.desc(), models.Route.name).all()


@router.post("/routes", response_model=schemas.RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(
    data: schemas.RouteCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Create a new route assignment."""
    route = models.Route(**data.model_dump())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.put("/routes/{route_id}", response_model=schemas.RouteOut)
def update_route(
    route_id: int,
    data: schemas.RouteUpdate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update a route's details."""
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(route, field, value)

    db.commit()
    db.refresh(route)
    return route


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Delete a route."""
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()


# ---------------------------------------------------------------------------
# Missed Pickups
# ---------------------------------------------------------------------------

@router.get("/missed-pickups", response_model=list[schemas.MissedPickupOut])
def get_missed_pickups(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all missed pickup reports."""
    return db.query(models.MissedPickup).order_by(models.MissedPickup.reported_at.desc()).all()


@router.post("/missed-pickups", response_model=schemas.MissedPickupOut, status_code=status.HTTP_201_CREATED)
def report_missed_pickup(
    data: schemas.MissedPickupCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Driver or manager reports a missed pickup."""
    pickup = models.MissedPickup(
        route_id=data.route_id,
        route_name=data.route_name,
        notes=data.notes,
        reported_by=current_user.id,
        assigned_to=data.assigned_to,
        manager_approved=False,
    )
    db.add(pickup)
    db.commit()
    db.refresh(pickup)
    return pickup


@router.put("/missed-pickups/{pickup_id}/approve", response_model=schemas.MissedPickupOut)
def approve_missed_pickup(
    pickup_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Manager approves a missed pickup report."""
    pickup = db.query(models.MissedPickup).filter(models.MissedPickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Missed pickup not found")
    pickup.manager_approved = True
    db.commit()
    db.refresh(pickup)
    return pickup


# ---------------------------------------------------------------------------
# Approval Queue
# ---------------------------------------------------------------------------

@router.get("/approvals", response_model=list[schemas.ApprovalQueueOut])
def get_approvals(
    status_filter: str = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return items in the approval queue."""
    query = db.query(models.ApprovalQueue)
    if status_filter:
        query = query.filter(models.ApprovalQueue.status == status_filter)
    return query.order_by(models.ApprovalQueue.created_at.desc()).all()


@router.put("/approvals/{approval_id}", response_model=schemas.ApprovalQueueOut)
def action_approval(
    approval_id: int,
    data: schemas.ApprovalActionRequest,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Manager approves or rejects an approval queue item."""
    item = db.query(models.ApprovalQueue).filter(models.ApprovalQueue.id == approval_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Approval item not found")

    if data.action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    item.status = data.action
    item.resolved_by = current_user.id
    item.resolved_at = datetime.now(timezone.utc)
    if data.manager_notes:
        item.manager_notes = data.manager_notes

    db.commit()
    db.refresh(item)
    return item
