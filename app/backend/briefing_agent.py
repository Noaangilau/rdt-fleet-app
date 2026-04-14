"""
briefing_agent.py — Morning Ops Briefing Agent for RDT Inc.

Runs on a daily schedule (configured via BriefingSettings). Assembles a live
fleet context snapshot, asks Claude to write a concise morning briefing for the
manager, sends it via email, and logs the result to BriefingLog.

Three public functions:
  generate_briefing(db)       — returns the briefing text string
  send_email(to, text)        — sends via SMTP, returns (success, error)
  run_morning_briefing()      — full job: generate + send + log
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_ENV_PATH, override=True)

import anthropic
from sqlalchemy.orm import Session

from database import SessionLocal
from ai_assistant import assemble_context, CLAUDE_MODEL
import models

logger = logging.getLogger(__name__)

BRIEFING_SYSTEM_PROMPT = """You are FleetBot, the AI assistant for RDT Inc.'s fleet management system.
The manager is about to start their workday. Write a concise morning operations briefing — no more than 150 words.

Cover only the most important items from the fleet data:
1. Any trucks with RED (overdue) maintenance that need action today
2. Any open HIGH-severity incidents
3. How many drivers are checked in vs. expected
4. Any routes that are unassigned or at risk
5. Any documents expiring within 7 days

Be direct and actionable. Start with the most critical issue. If everything looks good, say so briefly.
Do not use bullet points — write in short, clear sentences like a text message from a colleague."""


def generate_briefing(db: Session) -> str:
    """
    Assemble live fleet context and ask Claude to produce a morning briefing.
    Returns the briefing text, or an error string if the API call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return "AI briefing unavailable — ANTHROPIC_API_KEY not configured."

    try:
        fleet_context = assemble_context(db)
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            system=fleet_context,
            messages=[{"role": "user", "content": "Write today's morning ops briefing."}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Briefing generation failed: {e}")
        return f"Briefing generation failed: {str(e)}"


def send_email(to_address: str, briefing_text: str) -> tuple[bool, str | None]:
    """
    Send the morning briefing via SMTP.
    Reads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD from environment.
    Returns (success: bool, error_message: str | None).
    """
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()

    if not all([smtp_host, smtp_user, smtp_password, to_address]):
        return False, "SMTP not configured — set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env"

    try:
        today_str = datetime.now().strftime("%A, %B %-d")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"RDT Morning Briefing — {today_str}"
        msg["From"] = smtp_user
        msg["To"] = to_address

        # Plain text part
        plain = MIMEText(briefing_text, "plain")

        # HTML part with simple styling
        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: #68ccd1; color: white; padding: 12px 20px; border-radius: 8px 8px 0 0;">
            <strong>RDT Inc. — Morning Fleet Briefing</strong><br>
            <small>{today_str}</small>
          </div>
          <div style="background: #f9f9f9; border: 1px solid #e0e0e0; border-top: none;
                      padding: 20px; border-radius: 0 0 8px 8px; line-height: 1.6; color: #333;">
            {briefing_text.replace(chr(10), '<br>')}
          </div>
          <p style="font-size: 11px; color: #999; margin-top: 12px;">
            Sent by FleetBot · RDT Inc. Fleet Management · Vernal, UT
          </p>
        </body></html>
        """
        html = MIMEText(html_body, "html")

        msg.attach(plain)
        msg.attach(html)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_address, msg.as_string())

        return True, None

    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False, str(e)


def run_morning_briefing():
    """
    Main job function called by APScheduler each morning.

    Opens its own DB session (schedulers run outside the request lifecycle),
    reads BriefingSettings, generates a briefing via Claude, attempts to send
    it by email, and writes the result to BriefingLog regardless of outcome.
    """
    # Reload .env every time so Railway / uvicorn subprocess always gets fresh values
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

    db: Session = SessionLocal()
    try:
        settings = db.query(models.BriefingSettings).first()
        if not settings or not settings.enabled:
            logger.info("Morning briefing is disabled — skipping.")
            return

        logger.info("Running morning ops briefing...")

        # Generate briefing text via Claude
        briefing_text = generate_briefing(db)

        # Attempt email send
        email_to = settings.email_address.strip() if settings.email_address else ""
        success, error = send_email(email_to, briefing_text) if email_to else (
            False, "No email address configured in Settings"
        )

        # Log the result
        log_entry = models.BriefingLog(
            briefing_text=briefing_text,
            email_sent_to=email_to or None,
            success=success,
            error_message=error,
        )
        db.add(log_entry)
        db.commit()

        if success:
            logger.info(f"Morning briefing sent to {email_to}")
        else:
            logger.warning(f"Morning briefing generated but email failed: {error}")

    except Exception as e:
        logger.error(f"run_morning_briefing failed: {e}")
        db.rollback()
    finally:
        db.close()
