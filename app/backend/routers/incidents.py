"""
incidents.py — Incident report endpoints.

GET  /api/incidents      — list all incidents (manager), sorted by severity
POST /api/incidents      — submit a new incident (driver)
GET  /api/incidents/{id} — get a single incident
PUT  /api/incidents/{id} — update status / add resolution notes (manager)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
import models
import schemas
from auth import require_manager, require_driver

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

# Sort order for severity — high comes first
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _build_incident_out(incident: models.IncidentReport, db: Session) -> schemas.IncidentOut:
    """Helper: add truck_number to the incident response."""
    truck = db.query(models.Truck).filter(models.Truck.id == incident.truck_id).first()
    return schemas.IncidentOut(
        id=incident.id,
        truck_id=incident.truck_id,
        truck_number=truck.truck_number if truck else None,
        driver_name=incident.driver_name,
        incident_date=incident.incident_date,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        resolution_notes=incident.resolution_notes,
        resolved_at=incident.resolved_at,
        created_at=incident.created_at,
    )


@router.get("", response_model=list[schemas.IncidentOut])
def get_incidents(
    status_filter: str = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Return all incidents sorted by severity (high → medium → low), then by date.
    Optionally filter by status: ?status_filter=open
    """
    query = db.query(models.IncidentReport)
    if status_filter:
        query = query.filter(models.IncidentReport.status == status_filter)

    incidents = query.order_by(models.IncidentReport.created_at.desc()).all()

    # Sort by severity priority, then by date (newest first within same severity)
    incidents.sort(key=lambda i: (SEVERITY_ORDER.get(i.severity, 99), -i.created_at.timestamp()))
    return [_build_incident_out(i, db) for i in incidents]


@router.post("", response_model=schemas.IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: schemas.IncidentCreate,
    current_user: models.User = Depends(require_driver),
    db: Session = Depends(get_db),
):
    """Driver submits a new incident report."""
    truck = db.query(models.Truck).filter(models.Truck.id == data.truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    if data.severity not in ("low", "medium", "high"):
        raise HTTPException(status_code=400, detail="Severity must be low, medium, or high")

    incident = models.IncidentReport(
        truck_id=data.truck_id,
        driver_name=current_user.full_name or current_user.username,
        incident_date=data.incident_date,
        description=data.description,
        severity=data.severity,
        status="open",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return _build_incident_out(incident, db)


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(
    incident_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return a single incident by ID."""
    incident = db.query(models.IncidentReport).filter(
        models.IncidentReport.id == incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _build_incident_out(incident, db)


@router.put("/{incident_id}", response_model=schemas.IncidentOut)
def update_incident(
    incident_id: int,
    data: schemas.IncidentUpdate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Manager updates the incident status and optionally adds resolution notes."""
    incident = db.query(models.IncidentReport).filter(
        models.IncidentReport.id == incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if data.status:
        valid_statuses = ("open", "in_review", "resolved")
        if data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")
        incident.status = data.status
        # Record resolution timestamp when marked as resolved
        if data.status == "resolved" and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)

    if data.resolution_notes is not None:
        incident.resolution_notes = data.resolution_notes

    db.commit()
    db.refresh(incident)
    return _build_incident_out(incident, db)
