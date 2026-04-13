from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class IncidentCreate(BaseModel):
    truck_id: int
    incident_date: date
    description: str
    severity: str


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    truck_id: int
    truck_number: Optional[str] = None
    driver_name: str
    incident_date: date
    description: str
    severity: str
    status: str
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
