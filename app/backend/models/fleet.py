from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


MAINTENANCE_ITEM_TYPES = [
    "oil_change", "transmission_fluid", "brake_fluid", "coolant",
    "power_steering_fluid", "wheel_alignment", "brake_pads", "tire_wear", "windshield_wipers",
]

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

DEFAULT_INTERVALS = {
    "oil_change":            {"miles": 5000,  "days": 180},
    "transmission_fluid":    {"miles": 30000, "days": 730},
    "brake_fluid":           {"miles": 0,     "days": 730},
    "coolant":               {"miles": 30000, "days": 730},
    "power_steering_fluid":  {"miles": 50000, "days": 1095},
    "wheel_alignment":       {"miles": 12000, "days": 365},
    "brake_pads":            {"miles": 20000, "days": 730},
    "tire_wear":             {"miles": 10000, "days": 180},
    "windshield_wipers":     {"miles": 0,     "days": 365},
}


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    truck_number = Column(String(20), unique=True, nullable=False, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    truck_type = Column(String(50), nullable=True)
    current_mileage = Column(Integer, nullable=False, default=0)
    vin = Column(String(17), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    maintenance_items = relationship("MaintenanceItem", back_populates="truck", cascade="all, delete-orphan")
    incidents = relationship("IncidentReport", back_populates="truck", cascade="all, delete-orphan")
    mileage_logs = relationship("MileageLog", back_populates="truck", cascade="all, delete-orphan")
    repair_appointments = relationship("RepairAppointment", back_populates="truck", cascade="all, delete-orphan")
    fuel_logs = relationship("FuelLog", back_populates="truck", cascade="all, delete-orphan")
    repair_costs = relationship("RepairCost", back_populates="truck", cascade="all, delete-orphan")


class MaintenanceItem(Base):
    __tablename__ = "maintenance_items"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    item_type = Column(String(50), nullable=False)
    last_service_mileage = Column(Integer, nullable=True)
    last_service_date = Column(Date, nullable=True)
    interval_miles = Column(Integer, nullable=False)
    interval_days = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="maintenance_items")


class MileageLog(Base):
    __tablename__ = "mileage_logs"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    reported_mileage = Column(Integer, nullable=False)
    reported_by = Column(String(100), nullable=False)
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="mileage_logs")


class RepairAppointment(Base):
    __tablename__ = "repair_appointments"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incident_reports.id"), nullable=True)
    scheduled_date = Column(Date, nullable=False)
    mechanic_name = Column(String(100), nullable=True)
    mechanic_phone = Column(String(30), nullable=True)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending_approval")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    truck = relationship("Truck", back_populates="repair_appointments")


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    gallons = Column(Float, nullable=False)
    cost_per_gallon = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    odometer_at_fillup = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    truck = relationship("Truck", back_populates="fuel_logs")


class RepairCost(Base):
    __tablename__ = "repair_costs"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("repair_appointments.id"), nullable=True)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Float, nullable=False)
    vendor = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    truck = relationship("Truck", back_populates="repair_costs")
