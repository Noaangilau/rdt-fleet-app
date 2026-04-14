from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# --- Trucks ---

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
    id: int
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str]

    class Config:
        from_attributes = True


# --- Maintenance ---

class MaintenanceItemOut(BaseModel):
    id: int
    truck_id: int
    item_type: str
    item_label: str
    last_service_mileage: Optional[int]
    last_service_date: Optional[date]
    interval_miles: int
    interval_days: int
    notes: Optional[str]
    next_due_mileage: Optional[int]
    next_due_date: Optional[date]
    miles_remaining: Optional[int]
    days_remaining: Optional[int]
    status: str

    class Config:
        from_attributes = True


class RecordServiceRequest(BaseModel):
    last_service_mileage: Optional[int] = None
    last_service_date: Optional[date] = None
    notes: Optional[str] = None
    interval_miles: Optional[int] = None
    interval_days: Optional[int] = None


# --- Mileage ---

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


# --- Repair Appointments ---

class RepairAppointmentCreate(BaseModel):
    incident_id: Optional[int] = None
    scheduled_date: date
    mechanic_name: Optional[str] = None
    mechanic_phone: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class RepairAppointmentUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    mechanic_name: Optional[str] = None
    mechanic_phone: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class RepairAppointmentOut(BaseModel):
    id: int
    truck_id: int
    truck_number: Optional[str] = None
    incident_id: Optional[int]
    scheduled_date: date
    mechanic_name: Optional[str]
    mechanic_phone: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    status: str
    created_at: datetime
    approved_by: Optional[int]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Fuel Logs ---

class FuelLogCreate(BaseModel):
    date: date
    gallons: float
    cost_per_gallon: float
    odometer_at_fillup: Optional[int] = None
    notes: Optional[str] = None


class FuelLogOut(BaseModel):
    id: int
    truck_id: int
    truck_number: Optional[str] = None
    driver_id: int
    driver_name: Optional[str] = None
    date: date
    gallons: float
    cost_per_gallon: float
    total_cost: float
    odometer_at_fillup: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True


# --- Repair Costs ---

class RepairCostCreate(BaseModel):
    appointment_id: Optional[int] = None
    date: date
    description: str
    cost: float
    vendor: Optional[str] = None
    notes: Optional[str] = None


class RepairCostOut(BaseModel):
    id: int
    truck_id: int
    truck_number: Optional[str] = None
    appointment_id: Optional[int]
    date: date
    description: str
    cost: float
    vendor: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


# --- Fleet Cost Summary ---

class TruckCostSummary(BaseModel):
    truck_id: int
    truck_number: str
    total_repair_cost: float
    total_fuel_cost: float
    total_cost: float
    repair_entries: int
    fuel_entries: int
