"""
ai_assistant.py — AI assistant powered by Claude.

On every chat message, assembles a full context snapshot of the fleet
(all trucks, maintenance statuses, incidents) and injects it into
Claude's system prompt. This ensures every answer is based on live data.

For 10-15 trucks, the full context is ~2,000-4,000 tokens — well within
Claude's limits and cheap to send on every message.
"""

import os
from datetime import date, timedelta
from sqlalchemy.orm import Session
import anthropic
import models
from maintenance_logic import calculate_item_status
from models import ITEM_TYPE_LABELS

# Claude model to use — specified in requirements
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def assemble_context(db: Session) -> str:
    """
    Build the full fleet context string to inject into Claude's system prompt.
    Queries all trucks, maintenance items, and incidents from the live database.
    """
    today = date.today()
    trucks = db.query(models.Truck).order_by(models.Truck.truck_number).all()

    # Identify trucks with red or yellow status for the overview
    red_trucks = []
    yellow_trucks = []

    truck_sections = []
    for truck in trucks:
        items = truck.maintenance_items
        item_lines = []
        worst = "green"

        for item in items:
            result = calculate_item_status(item, truck.current_mileage)
            status = result["status"]
            label = ITEM_TYPE_LABELS.get(item.item_type, item.item_type)

            # Build the status line for this maintenance item
            parts = [f"    - {label}: [{status.upper()}]"]
            if item.last_service_date:
                parts.append(f"Last: {item.last_service_date}")
            else:
                parts.append("Last: Never serviced")
            if item.last_service_mileage:
                parts.append(f"at {item.last_service_mileage:,} mi")
            if result["next_due_mileage"]:
                remaining = result["miles_remaining"] or 0
                parts.append(f"| Next due: {result['next_due_mileage']:,} mi ({remaining:+,} mi)")
            if result["next_due_date"]:
                days = result["days_remaining"] or 0
                parts.append(f"/ {result['next_due_date']} ({days:+d} days)")

            item_lines.append(" ".join(parts))

            # Track worst status
            if status == "red":
                worst = "red"
            elif status == "yellow" and worst != "red":
                worst = "yellow"

        if worst == "red":
            red_trucks.append(truck.truck_number)
        elif worst == "yellow":
            yellow_trucks.append(truck.truck_number)

        truck_section = (
            f"Truck {truck.truck_number} ({truck.year} {truck.make} {truck.model}"
            f"{', ' + truck.truck_type if truck.truck_type else ''}) — "
            f"{truck.current_mileage:,} miles\n"
            + "\n".join(item_lines)
        )
        truck_sections.append(truck_section)

    # Open incidents
    open_incidents = (
        db.query(models.IncidentReport)
        .filter(models.IncidentReport.status != "resolved")
        .order_by(models.IncidentReport.created_at.desc())
        .all()
    )
    truck_map = {t.id: t.truck_number for t in trucks}

    incident_lines = []
    for inc in open_incidents:
        tn = truck_map.get(inc.truck_id, f"Truck #{inc.truck_id}")
        incident_lines.append(
            f"  [{inc.severity.upper()}] {tn} — {inc.incident_date} — "
            f"{inc.driver_name}: {inc.description} (Status: {inc.status})"
        )

    # Driver availability
    drivers = db.query(models.User).filter(models.User.role == "driver", models.User.is_active == True).all()
    driver_lines = []
    for driver in drivers:
        avail = db.query(models.DriverAvailability).filter(
            models.DriverAvailability.driver_id == driver.id
        ).first()
        status_str = avail.status if avail else "off_duty"
        route_str = f" (Route: {avail.current_route})" if avail and avail.current_route else ""
        driver_lines.append(
            f"  {driver.full_name or driver.username}: {status_str}{route_str}"
        )

    # Today's routes
    today_routes = (
        db.query(models.Route)
        .filter(models.Route.date == today)
        .order_by(models.Route.name)
        .all()
    )
    route_lines = []
    for r in today_routes:
        driver_obj = db.query(models.User).filter(models.User.id == r.driver_id).first() if r.driver_id else None
        truck_obj = db.query(models.Truck).filter(models.Truck.id == r.truck_id).first() if r.truck_id else None
        parts = [f"  {r.name}:"]
        parts.append(f"Driver={driver_obj.full_name or driver_obj.username if driver_obj else 'Unassigned'}")
        parts.append(f"Truck={truck_obj.truck_number if truck_obj else 'Unassigned'}")
        if r.notes:
            parts.append(f"Notes={r.notes}")
        route_lines.append(" ".join(parts))

    # Pending approvals
    pending_approvals = (
        db.query(models.ApprovalQueue)
        .filter(models.ApprovalQueue.status == "pending")
        .all()
    )

    # Expiring documents (within 30 days)
    cutoff = today + timedelta(days=30)
    expiring_docs = (
        db.query(models.DriverDocument)
        .filter(
            models.DriverDocument.expiry_date != None,
            models.DriverDocument.expiry_date <= cutoff,
        )
        .order_by(models.DriverDocument.expiry_date)
        .all()
    )
    doc_lines = []
    for doc in expiring_docs:
        driver_obj = db.query(models.User).filter(models.User.id == doc.driver_id).first()
        days_left = (doc.expiry_date - today).days
        status_word = "EXPIRED" if days_left < 0 else f"expires in {days_left}d"
        doc_lines.append(
            f"  {driver_obj.full_name or driver_obj.username if driver_obj else 'Unknown'} — "
            f"{doc.document_type}: {status_word} ({doc.expiry_date})"
        )

    # Financial summary: last 30 days
    thirty_days_ago = today - timedelta(days=30)
    recent_fuel = db.query(models.FuelLog).filter(models.FuelLog.date >= thirty_days_ago).all()
    recent_repairs = db.query(models.RepairCost).filter(models.RepairCost.date >= thirty_days_ago).all()
    total_fuel_cost = sum(f.total_cost for f in recent_fuel)
    total_repair_cost = sum(r.cost for r in recent_repairs)

    # Build the full system prompt
    context = f"""You are FleetBot, the AI assistant for RDT Inc.'s fleet management system.
RDT Inc. is a family-owned waste removal company based in Vernal, Utah, serving Uintah, Duchesne, and surrounding basin counties. They have been in business for 27 years. Fleet types include fully automated garbage trucks, roll-off trucks, dumpster/compactor trucks.

Today's date: {today}

=== FLEET OVERVIEW ===
Total trucks: {len(trucks)}
Trucks needing immediate attention (RED status): {', '.join(red_trucks) if red_trucks else 'None'}
Trucks with upcoming maintenance (YELLOW status): {', '.join(yellow_trucks) if yellow_trucks else 'None'}

=== TRUCK MAINTENANCE DETAILS ===
(Status: GREEN = good, YELLOW = due soon within 15% of interval, RED = overdue)

{chr(10).join(truck_sections)}

=== OPEN INCIDENTS ===
{chr(10).join(incident_lines) if incident_lines else 'No open incidents.'}

=== DRIVER AVAILABILITY (TODAY) ===
{chr(10).join(driver_lines) if driver_lines else 'No drivers on record.'}

=== TODAY\'S ROUTES ===
{chr(10).join(route_lines) if route_lines else 'No routes scheduled for today.'}

=== PENDING APPROVALS ===
{len(pending_approvals)} item(s) awaiting manager approval.

=== EXPIRING DRIVER DOCUMENTS (next 30 days) ===
{chr(10).join(doc_lines) if doc_lines else 'No documents expiring in the next 30 days.'}

=== FLEET FINANCIALS (last 30 days) ===
Total fuel cost: ${total_fuel_cost:,.2f} ({len(recent_fuel)} fill-ups)
Total repair cost: ${total_repair_cost:,.2f} ({len(recent_repairs)} repair entries)
Combined fleet cost: ${total_fuel_cost + total_repair_cost:,.2f}

Answer questions concisely and accurately based on the data above.
Reference trucks by their truck number (e.g., T-01).
If asked about maintenance schedules, reference the specific mileage or date shown.
Be helpful and direct — the manager needs fast, accurate answers."""

    return context


def chat(message: str, history: list, db: Session) -> str:
    """
    Send a message to Claude with the full fleet context in the system prompt.

    Args:
        message:  The manager's current question
        history:  List of prior messages in this session [{"role": ..., "content": ...}]
        db:       Active database session for fetching live data

    Returns:
        Claude's response as a plain string
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return (
            "AI assistant is not configured. "
            "Please set the ANTHROPIC_API_KEY environment variable."
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Assemble fresh context from the live database
    system_prompt = assemble_context(db)

    # Build message history for Claude (prior turns + current message)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": message})

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
