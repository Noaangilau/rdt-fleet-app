from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DriverAvailability(Base):
    __tablename__ = "driver_availability"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="off_duty")  # on_duty, available, off_duty
    current_route = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    driver = relationship("User", foreign_keys=[driver_id])


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    assigned_driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=True)
    date = Column(Date, nullable=False)

    assigned_driver = relationship("User", foreign_keys=[assigned_driver_id])
    assigned_truck = relationship("Truck", foreign_keys=[assigned_truck_id])


class MissedPickup(Base):
    __tablename__ = "missed_pickups"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    route_name = Column(String(100), nullable=True)  # denormalized for easy display
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), nullable=False, default="open")  # open, assigned, resolved
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    manager_approved = Column(Boolean, default=False)

    reporter = relationship("User", foreign_keys=[reported_by])
    assignee = relationship("User", foreign_keys=[assigned_to])


class ApprovalQueue(Base):
    __tablename__ = "approval_queue"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # repair_appointment, missed_pickup_coverage, out_of_service, driver_assignment
    reference_id = Column(Integer, nullable=True)
    reference_table = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)  # JSON string with context
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_notes = Column(Text, nullable=True)

    resolver = relationship("User", foreign_keys=[resolved_by])
