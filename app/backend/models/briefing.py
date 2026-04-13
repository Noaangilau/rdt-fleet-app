"""
models/briefing.py — Models for the Morning Ops Briefing agent.

BriefingSettings: one row, stores the manager's config (enabled, time, email).
BriefingLog: one row per briefing sent, stores the generated text and send result.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from database import Base


class BriefingSettings(Base):
    __tablename__ = "briefing_settings"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    send_time = Column(String(5), default="05:30", nullable=False)  # "HH:MM" 24-hour
    email_address = Column(String(255), default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BriefingLog(Base):
    __tablename__ = "briefing_log"

    id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    briefing_text = Column(Text, nullable=False)
    email_sent_to = Column(String(255), nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    error_message = Column(String(500), nullable=True)
