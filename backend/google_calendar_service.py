"""
Google Calendar service for creating events from daily plan.
Used by Execution Agent after Supervisor approval (confidence >= threshold).
"""

import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from db import supabase

logger = logging.getLogger(__name__)

# Default timezone for events
DEFAULT_TIMEZONE = "Asia/Kolkata"


def get_calendar_service(access_token: str):
    """
    Initialize Google Calendar API client using user's OAuth access token.
    
    Args:
        access_token: Valid Google OAuth2 access token from Supabase
        
    Returns:
        Google Calendar API v3 service instance
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
    timezone: str = DEFAULT_TIMEZONE
) -> dict | None:
    """
    Create a single event in user's primary Google Calendar.
    
    Args:
        access_token: User's Google OAuth2 access token
        title: Event title/summary
        start_time: Start datetime (ISO 8601, e.g. 2026-03-05T07:00:00)
        end_time: End datetime (ISO 8601)
        timezone: IANA timezone (default Asia/Kolkata)
        
    Returns:
        Dict with event details on success, None on failure
    """
    try:
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
        
        result = service.events().insert(
            calendarId="primary",
            body=event,
        ).execute()
        
        logger.info(f"Calendar event created: {result.get('htmlLink')}")
        return {
            "event_id": result.get("id"),
            "html_link": result.get("htmlLink"),
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
        }
        
    except HttpError as e:
        logger.exception(f"Calendar API error: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error creating calendar event: {e}")
        return None


def fetch_user_access_token(user_id: str) -> str | None:
    """
    Fetch user's Google OAuth access_token from Supabase.
    Ensures token belongs to the authenticated user (security).
    
    Args:
        user_id: Authenticated user's ID from Supabase Auth
        
    Returns:
        access_token string or None if not found
    """
    if not user_id:
        return None
    
    try:
        # Try user_profile.access_token first
        r = supabase.table("user_profile").select("access_token").eq("id", user_id).limit(1).execute()
        if r.data and len(r.data) > 0 and r.data[0].get("access_token"):
            return r.data[0]["access_token"].strip()
        
        # Fallback: oauth_tokens table
        r = supabase.table("oauth_tokens").select("access_token").eq("id", user_id).eq("provider", "google").limit(1).execute()
        if r.data and len(r.data) > 0 and r.data[0].get("access_token"):
            return r.data[0]["access_token"].strip()
            
    except Exception as e:
        logger.warning(f"Could not fetch access_token for user_id={user_id}: {e}")
    
    return None


def log_execution(user_id: str, event_title: str, start_time: str, end_time: str) -> None:
    """
    Store executed event in execution_logs table.
    
    Args:
        user_id: User ID
        event_title: Event title
        start_time: Start time (ISO 8601)
        end_time: End time (ISO 8601)
    """
    if not user_id:
        return
    
    try:
        supabase.table("execution_logs").insert({
            "user_id": user_id,
            "event_title": event_title,
            "start_time": start_time,
            "end_time": end_time,
        }).execute()
    except Exception as e:
        logger.warning(f"Could not write execution_logs: {e}")


def convert_time_to_iso(time_str: str, date: datetime = None) -> str:
    """
    Convert time string (e.g. "06:00", "14:30", "7:00 AM") to ISO 8601 datetime.
    
    Args:
        time_str: Time in HH:MM or "h:mm AM/PM" format
        date: Date to use (defaults to today)
        
    Returns:
        ISO 8601 datetime string
    """
    if date is None:
        date = datetime.now()
    raw = (time_str or "").strip()
    if not raw:
        return date.isoformat()

    try:
        upper = raw.upper()
        is_pm = "PM" in upper
        is_am = "AM" in upper
        if is_pm or is_am:
            # Remove AM/PM and parse
            part = upper.replace("PM", "").replace("AM", "").strip()
            hour, minute = map(int, part.split(":"))
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
        else:
            hour, minute = map(int, raw.split(":"))
        dt = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error converting time {time_str}: {e}")
        return date.isoformat()


def execute_daily_plan_to_calendar(user_id: str, events: list[dict]) -> dict:
    """
    Execute daily plan by creating events in user's Google Calendar.
    
    Flow:
    1. Fetch user's access_token from Supabase
    2. Loop through events
    3. Convert times to ISO datetime
    4. Calculate end_time from next event
    5. Create calendar event
    6. Log to execution_logs
    
    Args:
        user_id: Authenticated user ID
        events: List of dicts with 'title' and 'time' keys
        
    Returns:
        Dict with status and events_created count
    """
    # Security: fetch token for authenticated user only
    access_token = fetch_user_access_token(user_id)
    if not access_token:
        logger.warning(f"[calendar] No access token for user_id={user_id}, skipping calendar execution")
        return {
            "status": "error",
            "message": "No Google Calendar access token found. Please connect your Google Calendar.",
            "events_created": 0
        }
    
    created_count = 0
    results = []
    today = datetime.now()
    
    for i, event in enumerate(events):
        title = event.get("title", "Event")
        time_str = event.get("time", "")
        
        if not time_str:
            continue
        
        # Convert start time
        start_time = convert_time_to_iso(time_str, today)
        
        # Calculate end time from next event or default to 1 hour later
        if i < len(events) - 1:
            next_time_str = events[i + 1].get("time", "")
            if next_time_str:
                end_time = convert_time_to_iso(next_time_str, today)
            else:
                end_dt = datetime.fromisoformat(start_time) + timedelta(hours=1)
                end_time = end_dt.isoformat()
        else:
            # Last event: default to 23:59
            end_time = convert_time_to_iso("23:59", today)
        
        # Create calendar event
        result = create_calendar_event(
            access_token,
            title,
            start_time,
            end_time
        )
        
        if result:
            created_count += 1
            results.append(result)
            # Log to execution_logs
            log_execution(user_id, title, start_time, end_time)
    
    return {
        "status": "success",
        "events_created": created_count,
        "results": results
    }
