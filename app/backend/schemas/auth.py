from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    role: str = "driver"


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
