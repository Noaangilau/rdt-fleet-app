"""
models.py — SQLAlchemy ORM models for the RDT Inc. fleet management system.

Tables:
  - User:            Manager and driver accounts
  - Truck:           Fleet vehicles
  - MaintenanceItem: One row per (truck, item_type) — 9 items per truck
  - IncidentReport:  Driver-submitted issues
  - MileageLog:      Audit trail of every mileage update
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """App users — either a manager or a driver."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=True)
    # role: "manager" can access all features; "driver" can only submit mileage/incidents
    role = Column(String(10), nullable=False, default="driver")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Truck(Base):
    """A fleet vehicle owned by RDT Inc."""
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    # Human-readable identifier shown throughout the UI, e.g. "T-01"
    truck_number = Column(String(20), unique=True, nullable=False, index=True)
    make = Column(String(50), nullable=False)        # e.g. "Mack"
    model = Column(String(50), nullable=False)       # e.g. "LR Series"
    year = Column(Integer, nullable=False)
    truck_type = Column(String(50), nullable=True)   # e.g. "Garbage Truck", "Roll-Off"
    current_mileage = Column(Integer, nullable=False, default=0)
    vin = Column(String(17), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships — deleting a truck cascades to its maintenance items and incidents
    maintenance_items = relationship(
        "MaintenanceItem", back_populates="truck", cascade="all, delete-orphan"
    )
    incidents = relationship(
        "IncidentReport", back_populates="truck", cascade="all, delete-orphan"
    )
    mileage_logs = relationship(
        "MileageLog", back_populates="truck", cascade="all, delete-orphan"
    )


# The 9 fixed maintenance item types tracked for every truck
MAINTENANCE_ITEM_TYPES = [
    "oil_change",
    "transmission_fluid",
    "brake_fluid",
    "coolant",
    "power_steering_fluid",
    "wheel_alignment",
    "brake_pads",
    "tire_wear",
    "windshield_wipers",
]

# Human-readable display names for each item type
ITEM_TYPE_LABELS = {
    "oil_change": "Oil Change",
    "transmission_fluid": "Transmission Fluid",
    "brake_fluid": "Brake Fluid",
    "coolant": "Coolant",
    "power_steering_fluid": "Power Steering Fluid",
    "wheel_alignment": "Wheel Alignment",
    "brake_pads": "Brake Pads",
    "tire_wear": "Tire Wear / Rotation",
    "windshield_wipers": "Windshield Wipers",
}

# Default service intervals per item type
# interval_miles=0 means miles-based tracking is disabled (time-only items)
DEFAULT_INTERVALS = {
    "oil_change":            {"miles": 5000,  "days": 180},
    "transmission_fluid":    {"miles": 30000, "days": 730},
    "brake_fluid":           {"miles": 0,     "days": 730},   # time-only
    "coolant":               {"miles": 30000, "days": 730},
    "power_steering_fluid":  {"miles": 50000, "days": 1095},
    "wheel_alignment":       {"miles": 12000, "days": 365},
    "brake_pads":            {"miles": 20000, "days": 730},
    "tire_wear":             {"miles": 10000, "days": 180},
    "windshield_wipers":     {"miles": 0,     "days": 365},   # time-only
}


class MaintenanceItem(Base):
    """
    One maintenance record per (truck, item_type) pair.
    Stores the last service date/mileage and the service intervals.
    Status (green/yellow/red) is computed at query time in maintenance_logic.py.
    """
    __tablename__ = "maintenance_items"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    # One of the 9 values in MAINTENANCE_ITEM_TYPES
    item_type = Column(String(50), nullable=False)
    # Null means this item has never been serviced
    last_service_mileage = Column(Integer, nullable=True)
    last_service_date = Column(Date, nullable=True)
    # How often this item should be serviced (can be customized per truck)
    interval_miles = Column(Integer, nullable=False)
    interval_days = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="maintenance_items")


class IncidentReport(Base):
    """A driver-submitted incident or issue with a truck."""
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    driver_name = Column(String(100), nullable=False)   # pulled from logged-in user's full_name
    incident_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    # severity: "low" | "medium" | "high"
    severity = Column(String(10), nullable=False)
    # status: "open" | "in_review" | "resolved"
    status = Column(String(20), nullable=False, default="open")
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="incidents")


class MileageLog(Base):
    """Audit trail — every time a driver submits a mileage update it is recorded here."""
    __tablename__ = "mileage_logs"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    reported_mileage = Column(Integer, nullable=False)
    reported_by = Column(String(100), nullable=False)   # username of the submitting driver
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="mileage_logs")
