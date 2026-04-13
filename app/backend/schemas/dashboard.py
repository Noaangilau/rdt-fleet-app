from typing import Optional, List
from pydantic import BaseModel
from schemas.fleet import MileageLogOut
from schemas.incidents import IncidentOut


class TruckStatusSummary(BaseModel):
    id: int
    truck_number: str
    make: str
    model: str
    year: int
    truck_type: Optional[str]
    current_mileage: int
    overall_status: str
    red_count: int
    yellow_count: int
    green_count: int


class DashboardResponse(BaseModel):
    total_trucks: int
    trucks_needing_attention: int
    total_red_items: int
    total_yellow_items: int
    total_green_items: int
    truck_summaries: List[TruckStatusSummary]
    open_incidents: List[IncidentOut]
    recent_mileage_logs: List[MileageLogOut]
    pending_approvals_count: int = 0
    drivers_on_duty: int = 0
    expiring_documents_count: int = 0


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
