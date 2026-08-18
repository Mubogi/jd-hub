"""
Google Meet integration via the Google Calendar API.

Creates a Calendar event with an attached Google Meet conference link using a
service account. The service-account JSON key + calendar ID are provided via
environment variables (GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_CALENDAR_ID).

When the credentials are absent (e.g. before the user has created a service
account), every function below degrades gracefully so the enrolment/approval
flow still works — the admin just pastes a Meet link manually.
"""
from __future__ import annotations

import json
import os
import logging
from datetime import datetime, timedelta

from django.conf import settings

logger = logging.getLogger(__name__)

# Optional heavy imports — only needed when a service account is configured.
_discovered = False
_creds = None
_service = None


def _load_credentials():
    """Build a google Credentials object from the service-account JSON env var.

    Returns None if not configured (the graceful-degradation path).
    """
    global _discovered, _creds, _service
    if _discovered:
        return _creds
    _discovered = True

    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "").strip()
    if not key_json or not calendar_id:
        return None

    try:
        from google.oauth2 import service_account  # type: ignore
        info = json.loads(key_json)
        _creds = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
    except Exception as exc:
        logger.warning("Google service account not usable: %s", exc)
        _creds = None
    return _creds


def is_configured() -> bool:
    """True when a Google service account + calendar ID are configured."""
    return _load_credentials() is not None


def create_meet_link(
    summary: str,
    start_dt: datetime,
    duration_minutes: int = 60,
    attendee_email: str = "",
    description: str = "",
) -> str:
    """Create a Google Calendar event with a Meet link. Returns the Meet URL.

    Returns an empty string if Google is not configured (caller should then
    fall back to a manual link).
    """
    creds = _load_credentials()
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "").strip()
    if not creds or not calendar_id:
        return ""

    try:
        from googleapiclient.discovery import build  # type: ignore
    except Exception as exc:
        logger.warning("google-api-python-client not installed: %s", exc)
        return ""

    end_dt = start_dt + timedelta(minutes=duration_minutes)
    # Service accounts cannot invite attendees without Domain-Wide Delegation,
    # so we omit attendees here. The Meet link is emailed to the student
    # separately by the Django approve action via send_mail.
    body = {
        "summary": summary or "Jordan Design Hub class",
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Africa/Kampala"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Africa/Kampala"},
        "conferenceData": {
            "createRequest": {
                "requestId": f"jdhub-{start_dt.timestamp()}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        created = service.events().insert(
            calendarId=calendar_id,
            body=body,
            conferenceDataVersion=1,
        ).execute()
        # The Meet join URL lives under conferenceData.entryPoints.
        meet_url = ""
        conf = created.get("conferenceData", {})
        for ep in conf.get("entryPoints", []):
            if ep.get("entryPointType") == "video":
                meet_url = ep.get("uri", "")
                break
        return meet_url
    except Exception as exc:
        logger.error("Failed to create Google Meet link: %s", exc)
        return ""
