from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(10), nullable=False, default="driver")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
