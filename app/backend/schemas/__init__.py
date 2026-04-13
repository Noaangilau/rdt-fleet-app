# schemas/__init__.py — re-exports all schemas for backward compatibility
# Existing code using `import schemas; schemas.TruckOut` continues to work.

from schemas.auth import LoginRequest, TokenResponse, UserOut, CreateUserRequest, UpdateUserRequest
from schemas.fleet import (
    TruckCreate, TruckUpdate, TruckOut, TruckSummary,
    MaintenanceItemOut, RecordServiceRequest,
    MileageSubmit, MileageLogOut,
    RepairAppointmentCreate, RepairAppointmentUpdate, RepairAppointmentOut,
    FuelLogCreate, FuelLogOut,
    RepairCostCreate, RepairCostOut,
    TruckCostSummary,
)
from schemas.incidents import IncidentCreate, IncidentUpdate, IncidentOut
from schemas.operations import (
    AvailabilityUpdate, AvailabilityOut,
    RouteCreate, RouteUpdate, RouteOut,
    MissedPickupCreate, MissedPickupOut,
    ApprovalQueueOut, ApprovalActionRequest,
)
from schemas.hr import (
    DocumentCreate, DocumentUpdate, DocumentOut,
    AttendanceCreate, AttendanceOut,
    DriverNoteCreate, DriverNoteOut,
    DriverProfileOut,
)
from schemas.dashboard import TruckStatusSummary, DashboardResponse, ChatMessage, ChatRequest, ChatResponse
from schemas.notifications import NotificationOut, NotificationCountOut
from schemas.briefing import BriefingSettingsOut, BriefingSettingsUpdate, BriefingLogOut

__all__ = [
    "LoginRequest", "TokenResponse", "UserOut", "CreateUserRequest", "UpdateUserRequest",
    "TruckCreate", "TruckUpdate", "TruckOut", "TruckSummary",
    "MaintenanceItemOut", "RecordServiceRequest",
    "MileageSubmit", "MileageLogOut",
    "RepairAppointmentCreate", "RepairAppointmentUpdate", "RepairAppointmentOut",
    "FuelLogCreate", "FuelLogOut",
    "RepairCostCreate", "RepairCostOut", "TruckCostSummary",
    "IncidentCreate", "IncidentUpdate", "IncidentOut",
    "AvailabilityUpdate", "AvailabilityOut",
    "RouteCreate", "RouteUpdate", "RouteOut",
    "MissedPickupCreate", "MissedPickupOut",
    "ApprovalQueueOut", "ApprovalActionRequest",
    "DocumentCreate", "DocumentUpdate", "DocumentOut",
    "AttendanceCreate", "AttendanceOut",
    "DriverNoteCreate", "DriverNoteOut", "DriverProfileOut",
    "TruckStatusSummary", "DashboardResponse",
    "ChatMessage", "ChatRequest", "ChatResponse",
    "NotificationOut", "NotificationCountOut",
    "BriefingSettingsOut", "BriefingSettingsUpdate", "BriefingLogOut",
]
