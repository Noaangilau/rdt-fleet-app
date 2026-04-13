from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class AvailabilityUpdate(BaseModel):
    status: str  # on_duty, available, off_duty
    current_route: Optional[str] = None
    user_id: Optional[int] = None  # managers can set for a specific driver


class AvailabilityOut(BaseModel):
    id: int
    driver_id: int
    driver_name: Optional[str] = None
    username: Optional[str] = None
    status: str
    current_route: Optional[str] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    name: str
    description: Optional[str] = None
    assigned_driver_id: Optional[int] = None
    assigned_truck_id: Optional[int] = None
    date: date


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    assigned_driver_id: Optional[int] = None
    assigned_truck_id: Optional[int] = None
    date: Optional[date] = None


class RouteOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    assigned_driver_id: Optional[int] = None
    assigned_driver_name: Optional[str] = None
    assigned_truck_id: Optional[int] = None
    assigned_truck_number: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


class MissedPickupCreate(BaseModel):
    route_id: Optional[int] = None
    route_name: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None  # user_id to assign to


class MissedPickupOut(BaseModel):
    id: int
    route_id: Optional[int] = None
    route_name: Optional[str] = None
    reported_by: int
    reported_by_name: Optional[str] = None
    reported_at: Optional[datetime] = None
    status: str
    assigned_to: Optional[int] = None
    assigned_to_name: Optional[str] = None
    notes: Optional[str] = None
    manager_approved: bool

    class Config:
        from_attributes = True


class ApprovalQueueOut(BaseModel):
    id: int
    type: str
    reference_id: Optional[int] = None
    reference_table: Optional[str] = None
    details: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    manager_notes: Optional[str] = None

    class Config:
        from_attributes = True


class ApprovalActionRequest(BaseModel):
    action: str  # "approved" or "rejected"
    manager_notes: Optional[str] = None
