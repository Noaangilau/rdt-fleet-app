"""
hr.py — HR management endpoints.

GET    /api/hr/documents              — list all documents (filter by user_id optional)
POST   /api/hr/documents              — create a document record
PUT    /api/hr/documents/{id}         — update a document
DELETE /api/hr/documents/{id}         — delete a document
GET    /api/hr/attendance             — list attendance records
POST   /api/hr/attendance             — log an attendance entry
GET    /api/hr/notes                  — list driver notes
POST   /api/hr/notes                  — add a note for a driver
DELETE /api/hr/notes/{id}             — delete a note
GET    /api/hr/drivers/{id}/profile   — full driver profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import get_db
import models
import schemas
from auth import require_manager

router = APIRouter(prefix="/api/hr", tags=["hr"])


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

@router.get("/documents", response_model=list[schemas.DocumentOut])
def get_documents(
    user_id: int = None,
    expiring_days: int = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Return driver documents. Filter by user_id or documents expiring within N days.
    """
    query = db.query(models.DriverDocument)
    if user_id:
        query = query.filter(models.DriverDocument.driver_id == user_id)
    if expiring_days is not None:
        cutoff = date.today() + timedelta(days=expiring_days)
        query = query.filter(
            models.DriverDocument.expiry_date != None,
            models.DriverDocument.expiry_date <= cutoff,
        )
    return query.order_by(models.DriverDocument.expiry_date).all()


@router.post("/documents", response_model=schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    data: schemas.DocumentCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Add a document record for a driver."""
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    doc = models.DriverDocument(
        driver_id=data.user_id,
        document_type=data.document_type,
        expiry_date=data.expiry_date,
        document_number=data.document_number,
        notes=data.notes,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.put("/documents/{doc_id}", response_model=schemas.DocumentOut)
def update_document(
    doc_id: int,
    data: schemas.DocumentUpdate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update a document (e.g. renew expiry date)."""
    doc = db.query(models.DriverDocument).filter(models.DriverDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Delete a document record."""
    doc = db.query(models.DriverDocument).filter(models.DriverDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

@router.get("/attendance", response_model=list[schemas.AttendanceOut])
def get_attendance(
    user_id: int = None,
    from_date: date = None,
    to_date: date = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return attendance records with optional filters."""
    query = db.query(models.Attendance)
    if user_id:
        query = query.filter(models.Attendance.driver_id == user_id)
    if from_date:
        query = query.filter(models.Attendance.work_date >= from_date)
    if to_date:
        query = query.filter(models.Attendance.work_date <= to_date)
    return query.order_by(models.Attendance.work_date.desc()).all()


@router.post("/attendance", response_model=schemas.AttendanceOut, status_code=status.HTTP_201_CREATED)
def log_attendance(
    data: schemas.AttendanceCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Log an attendance entry for a driver."""
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = models.Attendance(
        driver_id=data.user_id,
        work_date=data.work_date or date.today(),
        status=data.status,
        shift_start=data.shift_start,
        shift_end=data.shift_end,
        notes=data.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Driver Notes
# ---------------------------------------------------------------------------

@router.get("/notes", response_model=list[schemas.DriverNoteOut])
def get_notes(
    user_id: int = None,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return manager notes about drivers."""
    query = db.query(models.DriverNote)
    if user_id:
        query = query.filter(models.DriverNote.driver_id == user_id)
    return query.order_by(models.DriverNote.created_at.desc()).all()


@router.post("/notes", response_model=schemas.DriverNoteOut, status_code=status.HTTP_201_CREATED)
def add_note(
    data: schemas.DriverNoteCreate,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Add a note about a driver."""
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    note = models.DriverNote(
        driver_id=data.user_id,
        note_text=data.note_text,
        created_by=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Delete a driver note."""
    note = db.query(models.DriverNote).filter(models.DriverNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()


# ---------------------------------------------------------------------------
# Driver Profile (aggregate view)
# ---------------------------------------------------------------------------

@router.get("/drivers/{user_id}/profile", response_model=schemas.DriverProfileOut)
def get_driver_profile(
    user_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return a full HR profile for a single driver."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "driver":
        raise HTTPException(status_code=404, detail="Driver not found")

    documents = db.query(models.DriverDocument).filter(
        models.DriverDocument.driver_id == user_id
    ).all()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.driver_id == user_id
    ).order_by(models.Attendance.work_date.desc()).limit(30).all()

    notes = db.query(models.DriverNote).filter(
        models.DriverNote.driver_id == user_id
    ).order_by(models.DriverNote.created_at.desc()).all()

    avail = db.query(models.DriverAvailability).filter(
        models.DriverAvailability.driver_id == user_id
    ).first()

    return schemas.DriverProfileOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        availability_status=avail.status if avail else "off_duty",
        documents=[schemas.DocumentOut.model_validate(d) for d in documents],
        recent_attendance=[schemas.AttendanceOut.model_validate(a) for a in attendance],
        notes=[schemas.DriverNoteOut.model_validate(n) for n in notes],
    )
