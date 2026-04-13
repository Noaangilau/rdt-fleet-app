"""
users.py — Driver account management endpoints (manager only).

GET    /api/users        — list all driver accounts
POST   /api/users        — create a new driver account
PUT    /api/users/{id}   — update name, password, or active status
DELETE /api/users/{id}   — deactivate a driver account
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import require_manager, hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return all user accounts (drivers and managers)."""
    return db.query(models.User).order_by(models.User.full_name).all()


@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: schemas.CreateUserRequest,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Manager creates a new driver (or manager) account."""
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{data.username}' is already taken",
        )

    if data.role not in ("driver", "manager"):
        raise HTTPException(status_code=400, detail="Role must be 'driver' or 'manager'")

    user = models.User(
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    data: schemas.UpdateUserRequest,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Update a user's name, password, or active status."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """
    Delete a user account.
    Managers cannot delete themselves.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
