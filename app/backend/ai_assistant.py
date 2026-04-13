"""
ai_assistant.py — AI assistant powered by Claude.

On every chat message, assembles a full context snapshot of the fleet
(all trucks, maintenance statuses, incidents) and injects it into
Claude's system prompt. This ensures every answer is based on live data.

For 10-15 trucks, the full context is ~2,000-4,000 tokens — well within
Claude's limits and cheap to send on every message.
"""

import os
from datetime import date
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

    # Build the full system prompt
    context = f"""You are FleetBot, the AI assistant for RDT Inc.'s fleet management system.
RDT Inc. is a family-owned waste removal company based in Vernal, Utah, serving Uintah, Duchesne, and surrounding basin counties. They have been in business for 27 years.

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
