"""
Google Calendar tool for the Tool Execution Agent.

Uses google-api-python-client and OAuth 2.0. Only invoked by the Tool Execution
Agent when Supervisor confidence >= threshold. Validates ISO datetimes and
inserts events into the primary calendar.
"""

import os
import re
import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ISO 8601 with optional timezone (Z or ±HH:MM)
_ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$"
)


def _validate_iso_datetime(value: str) -> tuple[bool, str]:
    """Validate ISO 8601 datetime string. Returns (ok, error_message)."""
    if not value or not isinstance(value, str):
        return False, "Datetime must be a non-empty string"
    value = value.strip()
    if not _ISO_DATETIME_RE.match(value):
        return False, (
            "Datetime must be ISO 8601 format, e.g. 2025-03-03T09:00:00Z or "
            "2025-03-03T09:00:00+05:30"
        )
    try:
        # Parse to ensure it's valid
        if value.endswith("Z"):
            value_parsed = value[:-1] + "+00:00"
        else:
            value_parsed = value
        datetime.fromisoformat(value_parsed.replace("Z", "+00:00"))
    except Exception as e:
        return False, f"Invalid datetime: {e}"
    return True, ""


class CalendarEventInput(BaseModel):
    """Structured input for a single calendar event."""

    title: str = Field(..., min_length=1, max_length=1024, description="Event title")
    start_time: str = Field(..., description="Start time in ISO 8601 (e.g. 2025-03-03T09:00:00Z)")
    end_time: str = Field(..., description="End time in ISO 8601")
    description: str = Field(default="", max_length=8192, description="Event description")


class CalendarEventResult(BaseModel):
    """Structured result of a calendar event creation attempt."""

    success: bool
    event_id: str | None = None
    html_link: str | None = None
    error: str | None = None
    title: str = ""
    start_time: str = ""
    end_time: str = ""


def _get_calendar_service(user_id: str | None = None):
    """
    Build Calendar API service with OAuth2 credentials.

    Credentials are loaded from:
    - Env: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN (single-user)
    - Optional: Supabase oauth_tokens table keyed by user_id for per-user tokens
    """
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip().strip("'\"")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip().strip("'\"")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip().strip("'\"")

    if not client_id or not client_secret:
        raise ValueError(
            "Missing Google OAuth credentials. Set GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in .env. See docs for OAuth setup."
        )

    # Per-user token from Supabase if available and user_id provided
    if user_id:
        try:
            from db import supabase  # noqa: PLC0415
            r = supabase.table("oauth_tokens").select(
                "access_token, refresh_token, expires_at"
            ).eq("id", user_id).eq("provider", "google").limit(1).execute()
            if r.data and len(r.data) > 0:
                row = r.data[0]
                creds = Credentials(
                    token=row.get("access_token"),
                    refresh_token=row.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=["https://www.googleapis.com/auth/calendar"],
                )
                if creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    # Optionally persist new tokens back to Supabase
                return build("calendar", "v3", credentials=creds, cache_discovery=False)
        except Exception as e:
            logger.warning("Supabase oauth_tokens not available for user %s: %s", user_id, e)

    if not refresh_token:
        raise ValueError(
            "No Google refresh token. Set GOOGLE_REFRESH_TOKEN in .env or configure "
            "oauth_tokens in Supabase for the user. Run OAuth flow once to obtain a refresh token."
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    from google.auth.transport.requests import Request
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    user_id: str | None = None,
) -> CalendarEventResult:
    """
    Insert a single event into the primary Google Calendar.

    Validates ISO 8601 datetimes, then inserts. Only call this through the
    Tool Execution Agent (no reasoning agent should call it directly).

    Returns structured success/failure.
    """
    ok, err = _validate_iso_datetime(start_time)
    if not ok:
        return CalendarEventResult(
            success=False,
            error=err,
            title=title,
            start_time=start_time,
            end_time=end_time,
        )
    ok, err = _validate_iso_datetime(end_time)
    if not ok:
        return CalendarEventResult(
            success=False,
            error=err,
            title=title,
            start_time=start_time,
            end_time=end_time,
        )

    # Ensure end > start (basic check via string comparison for ISO)
    if start_time >= end_time:
        return CalendarEventResult(
            success=False,
            error="end_time must be after start_time",
            title=title,
            start_time=start_time,
            end_time=end_time,
        )

    try:
        service = _get_calendar_service(user_id=user_id)
    except Exception as e:
        logger.exception("Failed to get Calendar service")
        return CalendarEventResult(
            success=False,
            error=str(e),
            title=title,
            start_time=start_time,
            end_time=end_time,
        )

    event_body = {
        "summary": title[:1024],
        "description": (description or "")[:8192],
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }

    try:
        from googleapiclient.errors import HttpError

        created = service.events().insert(
            calendarId="primary",
            body=event_body,
        ).execute()

        return CalendarEventResult(
            success=True,
            event_id=created.get("id"),
            html_link=created.get("htmlLink"),
            title=title,
            start_time=start_time,
            end_time=end_time,
        )
    except HttpError as e:
        err_msg = e.reason or str(e)
        if e.resp and e.resp.get("status") == 403:
            err_msg = "Calendar API access denied or quota exceeded. " + err_msg
        logger.exception("Calendar API error inserting event")
        return CalendarEventResult(
            success=False,
            error=err_msg,
            title=title,
            start_time=start_time,
            end_time=end_time,
        )
    except Exception as e:
        logger.exception("Unexpected error inserting calendar event")
        return CalendarEventResult(
            success=False,
            error=str(e),
            title=title,
            start_time=start_time,
            end_time=end_time,
        )


def create_calendar_event_tool(user_id: str | None = None):
    """
    Build a LangChain tool that inserts one event into Google Calendar.

    Use this from the Tool Execution Agent only. Accepts structured input,
    validates ISO datetimes, inserts into primary calendar, returns structured
    success/failure.
    """
    from langchain_core.tools import tool

    @tool
    def add_calendar_event(
        title: str,
        start_time: str,
        end_time: str,
        description: str = "",
    ) -> dict[str, Any]:
        """
        Insert a single event into the user's primary Google Calendar.

        Args:
            title: Event title (required).
            start_time: Start in ISO 8601 (e.g. 2025-03-03T09:00:00Z).
            end_time: End in ISO 8601.
            description: Optional event description.

        Returns:
            Dict with success (bool), event_id/html_link if success, error if failure.
        """
        result = create_calendar_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            user_id=user_id,
        )
        out = {
            "success": result.success,
            "title": result.title,
            "start_time": result.start_time,
            "end_time": result.end_time,
        }
        if result.success:
            out["event_id"] = result.event_id
            out["html_link"] = result.html_link
        else:
            out["error"] = result.error
        return out

    return add_calendar_event
