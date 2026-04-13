"""
fleet.py — Fleet financials: repair appointments, fuel logs, repair costs.

GET    /api/fleet/trucks/{truck_id}/repairs     — list repair appointments
POST   /api/fleet/trucks/{truck_id}/repairs     — schedule a repair
PUT    /api/fleet/repairs/{id}                  — update appointment
DELETE /api/fleet/repairs/{id}                  — delete appointment
GET    /api/fleet/trucks/{truck_id}/fuel        — list fuel log entries
POST   /api/fleet/trucks/{truck_id}/fuel        — log a fuel fill-up
GET    /api/fleet/trucks/{truck_id}/costs       — list repair cost entries
POST   /api/fleet/trucks/{truck_id}/costs       — add a repair cost
GET    /api/fleet/trucks/{truck_id}/cost-summary — aggregate cost totals for one truck
GET    /api/fleet/cost-summary                  — fleet-wide cost summary
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from auth import require_manager

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


def _get_truck_or_404(truck_id: int, db: Session) -> models.Truck:
    truck = db.query(models.Truck).filter(models.Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


# ---------------------------------------------------------------------------
# Repair Appointments
# ---------------------------------------------------------------------------

@router.get("/trucks/{truck_id}/repairs", response_model=list[schemas.RepairAppointmentOut])
def get_repairs(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all repair appointments for a truck."""
    _get_truck_or_404(truck_id, db)
    return (
        db.query(models.RepairAppointment)
        .filter(models.RepairAppointment.truck_id == truck_id)
        .order_by(models.RepairAppointment.scheduled_date.desc())
        .all()
    )


@router.post(
    "/trucks/{truck_id}/repairs",
    response_model=schemas.RepairAppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_repair(
    truck_id: int,
    data: schemas.RepairAppointmentCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Schedule a repair appointment for a truck."""
    _get_truck_or_404(truck_id, db)
    # Exclude truck_id from dump since it's passed separately
    fields = data.model_dump(exclude={"truck_id"})
    repair = models.RepairAppointment(truck_id=truck_id, **fields)
    db.add(repair)
    db.commit()
    db.refresh(repair)
    return repair


@router.put("/repairs/{repair_id}", response_model=schemas.RepairAppointmentOut)
def update_repair(
    repair_id: int,
    data: schemas.RepairAppointmentUpdate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update a repair appointment (status, notes, mechanic, etc.)."""
    repair = db.query(models.RepairAppointment).filter(
        models.RepairAppointment.id == repair_id
    ).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair appointment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(repair, field, value)

    db.commit()
    db.refresh(repair)
    return repair


@router.delete("/repairs/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repair(
    repair_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Delete a repair appointment."""
    repair = db.query(models.RepairAppointment).filter(
        models.RepairAppointment.id == repair_id
    ).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair appointment not found")
    db.delete(repair)
    db.commit()


# ---------------------------------------------------------------------------
# Fuel Logs
# ---------------------------------------------------------------------------

@router.get("/trucks/{truck_id}/fuel", response_model=list[schemas.FuelLogOut])
def get_fuel_logs(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all fuel log entries for a truck."""
    _get_truck_or_404(truck_id, db)
    return (
        db.query(models.FuelLog)
        .filter(models.FuelLog.truck_id == truck_id)
        .order_by(models.FuelLog.date.desc())
        .all()
    )


@router.post(
    "/trucks/{truck_id}/fuel",
    response_model=schemas.FuelLogOut,
    status_code=status.HTTP_201_CREATED,
)
def log_fuel(
    truck_id: int,
    data: schemas.FuelLogCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Log a fuel fill-up for a truck."""
    _get_truck_or_404(truck_id, db)
    total_cost = round(data.gallons * data.cost_per_gallon, 2)
    log = models.FuelLog(
        truck_id=truck_id,
        driver_id=current_user.id,
        date=data.date,
        gallons=data.gallons,
        cost_per_gallon=data.cost_per_gallon,
        total_cost=total_cost,
        odometer_at_fillup=data.odometer_at_fillup,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ---------------------------------------------------------------------------
# Repair Costs
# ---------------------------------------------------------------------------

@router.get("/trucks/{truck_id}/costs", response_model=list[schemas.RepairCostOut])
def get_repair_costs(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all repair cost entries for a truck."""
    _get_truck_or_404(truck_id, db)
    return (
        db.query(models.RepairCost)
        .filter(models.RepairCost.truck_id == truck_id)
        .order_by(models.RepairCost.date.desc())
        .all()
    )


@router.post(
    "/trucks/{truck_id}/costs",
    response_model=schemas.RepairCostOut,
    status_code=status.HTTP_201_CREATED,
)
def add_repair_cost(
    truck_id: int,
    data: schemas.RepairCostCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Record a repair cost for a truck."""
    _get_truck_or_404(truck_id, db)
    fields = data.model_dump(exclude={"truck_id"})
    cost = models.RepairCost(truck_id=truck_id, **fields)
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


@router.get("/trucks/{truck_id}/cost-summary", response_model=schemas.TruckCostSummary)
def get_truck_cost_summary(
    truck_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return aggregate cost totals for a single truck."""
    truck = _get_truck_or_404(truck_id, db)

    total_repair = db.query(func.sum(models.RepairCost.cost)).filter(
        models.RepairCost.truck_id == truck_id
    ).scalar() or 0.0

    total_fuel = db.query(func.sum(models.FuelLog.total_cost)).filter(
        models.FuelLog.truck_id == truck_id
    ).scalar() or 0.0

    repair_count = db.query(models.RepairCost).filter(
        models.RepairCost.truck_id == truck_id
    ).count()

    fuel_count = db.query(models.FuelLog).filter(
        models.FuelLog.truck_id == truck_id
    ).count()

    return schemas.TruckCostSummary(
        truck_id=truck_id,
        truck_number=truck.truck_number,
        total_repair_cost=round(total_repair, 2),
        total_fuel_cost=round(total_fuel, 2),
        total_cost=round(total_repair + total_fuel, 2),
        repair_entries=repair_count,
        fuel_entries=fuel_count,
    )


@router.get("/cost-summary", response_model=list[schemas.TruckCostSummary])
def get_fleet_cost_summary(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return aggregate cost totals for every truck in the fleet."""
    trucks = db.query(models.Truck).order_by(models.Truck.truck_number).all()
    summaries = []
    for truck in trucks:
        repair_total = db.query(func.sum(models.RepairCost.cost)).filter(
            models.RepairCost.truck_id == truck.id
        ).scalar() or 0.0

        fuel_total = db.query(func.sum(models.FuelLog.total_cost)).filter(
            models.FuelLog.truck_id == truck.id
        ).scalar() or 0.0

        summaries.append(schemas.TruckCostSummary(
            truck_id=truck.id,
            truck_number=truck.truck_number,
            total_repair_cost=round(repair_total, 2),
            total_fuel_cost=round(fuel_total, 2),
            total_cost=round(repair_total + fuel_total, 2),
            repair_entries=db.query(models.RepairCost).filter(models.RepairCost.truck_id == truck.id).count(),
            fuel_entries=db.query(models.FuelLog).filter(models.FuelLog.truck_id == truck.id).count(),
        ))
    return summaries
