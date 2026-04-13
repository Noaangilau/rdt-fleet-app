from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    user_id: int
    document_type: str  # cdl_license, medical_card, other
    expiry_date: Optional[date] = None
    document_number: Optional[str] = None
    notes: Optional[str] = None


class DocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    expiry_date: Optional[date] = None
    document_number: Optional[str] = None
    notes: Optional[str] = None


class DocumentOut(BaseModel):
    id: int
    driver_id: int
    driver_name: Optional[str] = None
    document_type: str
    expiry_date: Optional[date] = None
    document_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    user_id: int  # the driver being logged
    work_date: Optional[date] = None
    status: str  # present, absent, late, excused
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    notes: Optional[str] = None


class AttendanceOut(BaseModel):
    id: int
    driver_id: int
    driver_name: Optional[str] = None
    work_date: date
    status: str
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class DriverNoteCreate(BaseModel):
    user_id: int  # the driver this note is about
    note_text: str


class DriverNoteOut(BaseModel):
    id: int
    driver_id: int
    note_text: str
    created_by: int
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DriverProfileOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    availability_status: Optional[str] = None
    documents: List[DocumentOut] = []
    recent_attendance: List[AttendanceOut] = []
    notes: List[DriverNoteOut] = []

    class Config:
        from_attributes = True
