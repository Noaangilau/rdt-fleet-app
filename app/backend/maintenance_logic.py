"""
maintenance_logic.py — Status calculation engine for maintenance items.

The status (green/yellow/red) is never stored in the database.
It is computed fresh each time a maintenance item is queried,
based on the truck's current mileage and today's date.

Status thresholds:
  - red:    past due (mileage or date exceeded)
  - yellow: within 15% of the interval (due soon)
  - green:  more than 15% of interval remaining
"""

from datetime import date, timedelta
from typing import Optional
import models
from models import ITEM_TYPE_LABELS


# Priority used to pick the worst of two signals
STATUS_PRIORITY = {"red": 2, "yellow": 1, "green": 0}


def _miles_signal(item: models.MaintenanceItem, current_mileage: int) -> str:
    """
    Calculate the miles-based status for a single maintenance item.
    Returns "green", "yellow", or "red".
    If interval_miles is 0, miles tracking is disabled and we return "green".
    """
    if item.interval_miles == 0:
        return "green"   # miles tracking disabled for this item type

    if item.last_service_mileage is None:
        return "yellow"  # never serviced — flag it as due soon

    miles_remaining = (item.last_service_mileage + item.interval_miles) - current_mileage
    percent_remaining = miles_remaining / item.interval_miles

    if miles_remaining <= 0:
        return "red"
    elif percent_remaining <= 0.15:
        return "yellow"
    else:
        return "green"


def _time_signal(item: models.MaintenanceItem) -> str:
    """
    Calculate the time-based status for a single maintenance item.
    Returns "green", "yellow", or "red".
    If interval_days is 0, time tracking is disabled and we return "green".
    """
    if item.interval_days == 0:
        return "green"   # time tracking disabled for this item type

    if item.last_service_date is None:
        return "yellow"  # never serviced

    today = date.today()
    due_date = item.last_service_date + timedelta(days=item.interval_days)
    days_remaining = (due_date - today).days
    percent_remaining = days_remaining / item.interval_days

    if days_remaining <= 0:
        return "red"
    elif percent_remaining <= 0.15:
        return "yellow"
    else:
        return "green"


def calculate_item_status(item: models.MaintenanceItem, current_mileage: int) -> dict:
    """
    Compute the full status dict for a maintenance item.
    Returns a dict with status, computed due values, and remaining values.
    This is merged into the MaintenanceItemOut schema by the router.
    """
    miles_sig = _miles_signal(item, current_mileage)
    time_sig = _time_signal(item)

    # Final status is the worst of the two signals
    final_status = max(miles_sig, time_sig, key=lambda s: STATUS_PRIORITY[s])

    # Compute next due mileage
    next_due_mileage = None
    miles_remaining = None
    if item.interval_miles > 0 and item.last_service_mileage is not None:
        next_due_mileage = item.last_service_mileage + item.interval_miles
        miles_remaining = next_due_mileage - current_mileage

    # Compute next due date
    next_due_date = None
    days_remaining = None
    if item.interval_days > 0 and item.last_service_date is not None:
        next_due_date = item.last_service_date + timedelta(days=item.interval_days)
        days_remaining = (next_due_date - date.today()).days

    return {
        "status": final_status,
        "next_due_mileage": next_due_mileage,
        "next_due_date": next_due_date,
        "miles_remaining": miles_remaining,
        "days_remaining": days_remaining,
        "item_label": ITEM_TYPE_LABELS.get(item.item_type, item.item_type),
    }


def get_truck_overall_status(maintenance_items: list, current_mileage: int) -> dict:
    """
    Compute the overall status for a truck based on all its maintenance items.
    Returns a dict with overall_status, red_count, yellow_count, green_count.
    Used by the dashboard to show which trucks need attention.
    """
    counts = {"red": 0, "yellow": 0, "green": 0}
    for item in maintenance_items:
        result = calculate_item_status(item, current_mileage)
        counts[result["status"]] += 1

    # Overall status is the worst individual item status
    if counts["red"] > 0:
        overall = "red"
    elif counts["yellow"] > 0:
        overall = "yellow"
    else:
        overall = "green"

    return {
        "overall_status": overall,
        "red_count": counts["red"],
        "yellow_count": counts["yellow"],
        "green_count": counts["green"],
    }
