"""
Google Calendar service using the user's OAuth access token.

Used by the Execution Agent when the Supervisor approves a schedule (confidence > threshold).
Creates events in the user's primary calendar. Only invoked after Supervisor approval.
"""

import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Default timezone for event start/end (per requirements)
DEFAULT_TIMEZONE = "Asia/Kolkata"


def get_calendar_service(access_token: str):
    """
    Initialize Google Calendar API service using the user's OAuth access token.

    Args:
        access_token: Valid Google OAuth2 access token (from Supabase user_profile or oauth_tokens).

    Returns:
        Google Calendar API v3 service instance.
    """
    if not access_token or not access_token.strip():
        raise ValueError("access_token is required")
    creds = Credentials(token=access_token.strip())
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return service


def create_calendar_event(
    access_token: str,
    title: str,
    start_time: str,
    end_time: str,
    timezone: str = DEFAULT_TIMEZONE,
) -> str | None:
    """
    Create a single event in the user's primary Google Calendar.

    Args:
        access_token: User's Google OAuth2 access token.
        title: Event summary/title.
        start_time: Start datetime (ISO 8601 or compatible, e.g. 2026-03-05T07:00:00).
        end_time: End datetime (ISO 8601 or compatible).
        timezone: IANA timezone for the event (default Asia/Kolkata).

    Returns:
        Event htmlLink on success, None on failure (errors are logged).
    """
    service = get_calendar_service(access_token)
    event = {
        "summary": (title or "Event").strip()[:1024],
        "start": {
            "dateTime": start_time.strip(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time.strip(),
            "timeZone": timezone,
        },
    }
    try:
        result = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )
        link = result.get("htmlLink")
        logger.info("Calendar event created: %s", link)
        return link
    except HttpError as e:
        logger.exception("Calendar API error creating event: %s", e)
        return None
    except Exception as e:
        logger.exception("Unexpected error creating calendar event: %s", e)
        return None


def add_event_to_google_calendar(
    title: str,
    start_time: str,
    end_time: str,
    access_token: str,
) -> str:
    """
    Creates an event in the user's Google Calendar.
    LangChain tool wrapper: use from Execution Agent with the authenticated user's token.
    """
    link = create_calendar_event(access_token, title, start_time, end_time)
    if link:
        return f"Calendar event created: {link}"
    return "Failed to create calendar event."


def get_langchain_calendar_tool():
    """Build the LangChain @tool for Google Calendar event creation (takes access_token)."""
    from langchain_core.tools import tool

    @tool
    def add_event_to_google_calendar_tool(
        title: str,
        start_time: str,
        end_time: str,
        access_token: str,
    ) -> str:
        """Creates an event in the user's Google Calendar. Requires a valid OAuth access_token."""
        return add_event_to_google_calendar(
            title=title,
            start_time=start_time,
            end_time=end_time,
            access_token=access_token,
        )

    return add_event_to_google_calendar_tool
