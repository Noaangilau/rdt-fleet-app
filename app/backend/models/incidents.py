from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    driver_name = Column(String(100), nullable=False)
    incident_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="open")
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="incidents")
