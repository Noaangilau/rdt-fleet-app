from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # incident, missed_pickup, document_expiry, approval, checkin_reminder
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
