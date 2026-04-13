"""
schemas.py — Pydantic models for request validation and response serialization.

These define the shape of data going in and out of the API.
They are separate from the ORM models in models.py.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    """Manager uses this to create a new driver account."""
    username: str
    password: str
    full_name: Optional[str] = None
    role: str = "driver"   # defaults to driver; manager can set "manager" too

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Trucks
# ---------------------------------------------------------------------------

class TruckCreate(BaseModel):
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str] = None
    current_mileage: int = 0
    vin: Optional[str] = None
    notes: Optional[str] = None

class TruckUpdate(BaseModel):
    truck_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    truck_type: Optional[str] = None
    current_mileage: Optional[int] = None
    vin: Optional[str] = None
    notes: Optional[str] = None

class TruckOut(BaseModel):
    id: int
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str]
    current_mileage: int
    vin: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TruckSummary(BaseModel):
    """Lightweight truck info used in driver dropdowns."""
    id: int
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------

class MaintenanceItemOut(BaseModel):
    """A maintenance item with its computed status fields."""
    id: int
    truck_id: int
    item_type: str
    item_label: str                        # human-readable label, e.g. "Oil Change"
    last_service_mileage: Optional[int]
    last_service_date: Optional[date]
    interval_miles: int
    interval_days: int
    notes: Optional[str]
    # Computed fields (calculated in maintenance_logic.py)
    next_due_mileage: Optional[int]
    next_due_date: Optional[date]
    miles_remaining: Optional[int]
    days_remaining: Optional[int]
    status: str                            # "green" | "yellow" | "red"

    class Config:
        from_attributes = True

class RecordServiceRequest(BaseModel):
    """Update a maintenance item after a service is performed."""
    last_service_mileage: Optional[int] = None
    last_service_date: Optional[date] = None
    notes: Optional[str] = None
    # Optionally override the default intervals for this specific truck
    interval_miles: Optional[int] = None
    interval_days: Optional[int] = None


# ---------------------------------------------------------------------------
# Mileage
# ---------------------------------------------------------------------------

class MileageSubmit(BaseModel):
    truck_id: int
    mileage: int

class MileageLogOut(BaseModel):
    id: int
    truck_id: int
    reported_mileage: int
    reported_by: str
    reported_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

class IncidentCreate(BaseModel):
    truck_id: int
    incident_date: date
    description: str
    severity: str   # "low" | "medium" | "high"

class IncidentUpdate(BaseModel):
    """Manager updates the status and optionally adds resolution notes."""
    status: Optional[str] = None
    resolution_notes: Optional[str] = None

class IncidentOut(BaseModel):
    id: int
    truck_id: int
    truck_number: Optional[str] = None    # populated by the router
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


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TruckStatusSummary(BaseModel):
    """Per-truck summary used on the manager dashboard."""
    id: int
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str]
    current_mileage: int
    overall_status: str          # worst status across all 9 maintenance items
    red_count: int               # number of overdue items
    yellow_count: int            # number of due-soon items
    green_count: int

class DashboardResponse(BaseModel):
    total_trucks: int
    trucks_needing_attention: int    # trucks with at least one red item
    total_red_items: int
    total_yellow_items: int
    total_green_items: int
    truck_summaries: List[TruckStatusSummary]
    open_incidents: List[IncidentOut]
    recent_mileage_logs: List[MileageLogOut]


# ---------------------------------------------------------------------------
# AI Chat
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str      # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []   # conversation history from this session

class ChatResponse(BaseModel):
    response: str
