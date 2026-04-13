from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DriverDocument(Base):
    __tablename__ = "driver_documents"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String(30), nullable=False)  # cdl_license, medical_card, other
    expiry_date = Column(Date, nullable=True)
    document_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    driver = relationship("User", foreign_keys=[driver_id])


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, late, excused
    shift_start = Column(DateTime, nullable=True)
    shift_end = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    driver = relationship("User", foreign_keys=[driver_id])


class DriverNote(Base):
    __tablename__ = "driver_notes"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    driver = relationship("User", foreign_keys=[driver_id])
    author = relationship("User", foreign_keys=[created_by])
