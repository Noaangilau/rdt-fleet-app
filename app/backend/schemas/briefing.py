"""
schemas/briefing.py — Pydantic schemas for the Morning Ops Briefing agent.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BriefingSettingsOut(BaseModel):
    id: int
    enabled: bool
    send_time: str
    email_address: str
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BriefingSettingsUpdate(BaseModel):
    enabled: bool
    send_time: str
    email_address: str


class BriefingLogOut(BaseModel):
    id: int
    sent_at: datetime
    briefing_text: str
    email_sent_to: Optional[str] = None
    success: bool
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}
