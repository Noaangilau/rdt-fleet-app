"""
dashboard.py — Manager dashboard overview endpoint.

GET /api/dashboard — returns fleet-wide status summary, open incidents,
                     and recent mileage activity
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import require_manager
from maintenance_logic import get_truck_overall_status
from routers.incidents import SEVERITY_ORDER

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardResponse)
def get_dashboard(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Assemble the full manager dashboard in a single request.
    Returns:
      - Per-truck status summaries (used for the truck grid)
      - Counts of red/yellow/green items across the entire fleet
      - Open incidents sorted by severity
      - The 10 most recent mileage log entries
    """
    trucks = db.query(models.Truck).order_by(models.Truck.truck_number).all()

    truck_summaries = []
    total_red = total_yellow = total_green = 0
    trucks_needing_attention = 0

    for truck in trucks:
        status_data = get_truck_overall_status(truck.maintenance_items, truck.current_mileage)

        total_red += status_data["red_count"]
        total_yellow += status_data["yellow_count"]
        total_green += status_data["green_count"]

        if status_data["overall_status"] == "red":
            trucks_needing_attention += 1

        truck_summaries.append(schemas.TruckStatusSummary(
            id=truck.id,
            truck_number=truck.truck_number,
            make=truck.make,
            model=truck.model,
            year=truck.year,
            truck_type=truck.truck_type,
            current_mileage=truck.current_mileage,
            overall_status=status_data["overall_status"],
            red_count=status_data["red_count"],
            yellow_count=status_data["yellow_count"],
            green_count=status_data["green_count"],
        ))

    # Open incidents sorted by severity (high → medium → low)
    open_incidents = (
        db.query(models.IncidentReport)
        .filter(models.IncidentReport.status != "resolved")
        .order_by(models.IncidentReport.created_at.desc())
        .all()
    )
    open_incidents.sort(
        key=lambda i: (SEVERITY_ORDER.get(i.severity, 99), -i.created_at.timestamp())
    )

    # Build incident responses with truck numbers
    truck_map = {t.id: t.truck_number for t in trucks}
    incident_outs = [
        schemas.IncidentOut(
            id=i.id,
            truck_id=i.truck_id,
            truck_number=truck_map.get(i.truck_id),
            driver_name=i.driver_name,
            incident_date=i.incident_date,
            description=i.description,
            severity=i.severity,
            status=i.status,
            resolution_notes=i.resolution_notes,
            resolved_at=i.resolved_at,
            created_at=i.created_at,
        )
        for i in open_incidents
    ]

    # 10 most recent mileage log entries
    recent_logs = (
        db.query(models.MileageLog)
        .order_by(models.MileageLog.reported_at.desc())
        .limit(10)
        .all()
    )

    return schemas.DashboardResponse(
        total_trucks=len(trucks),
        trucks_needing_attention=trucks_needing_attention,
        total_red_items=total_red,
        total_yellow_items=total_yellow,
        total_green_items=total_green,
        truck_summaries=truck_summaries,
        open_incidents=incident_outs,
        recent_mileage_logs=[
            schemas.MileageLogOut(
                id=log.id,
                truck_id=log.truck_id,
                reported_mileage=log.reported_mileage,
                reported_by=log.reported_by,
                reported_at=log.reported_at,
            )
            for log in recent_logs
        ],
    )
