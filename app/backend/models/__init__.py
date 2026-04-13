# models/__init__.py — imports all models so that:
# 1. SQLAlchemy registers them all with Base before create_all
# 2. Existing code like `import models; models.User` continues to work
# 3. `from models import User` continues to work

from models.user import User
from models.fleet import (
    Truck, MaintenanceItem, MileageLog, RepairAppointment, FuelLog, RepairCost,
    MAINTENANCE_ITEM_TYPES, ITEM_TYPE_LABELS, DEFAULT_INTERVALS,
)
from models.incidents import IncidentReport
from models.operations import DriverAvailability, Route, MissedPickup, ApprovalQueue
from models.hr import DriverDocument, Attendance, DriverNote
from models.notifications import Notification

__all__ = [
    "User",
    "Truck", "MaintenanceItem", "MileageLog", "RepairAppointment", "FuelLog", "RepairCost",
    "MAINTENANCE_ITEM_TYPES", "ITEM_TYPE_LABELS", "DEFAULT_INTERVALS",
    "IncidentReport",
    "DriverAvailability", "Route", "MissedPickup", "ApprovalQueue",
    "DriverDocument", "Attendance", "DriverNote",
    "Notification",
]
