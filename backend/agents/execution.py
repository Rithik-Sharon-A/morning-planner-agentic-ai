"""
Execution layer: runs plans (ride, meal) and optionally the Tool Execution Agent
for Google Calendar when Supervisor confidence >= threshold.

Flow: User Request → Supervisor Agent → Confidence Check → Execution Agent → Google Calendar Tool → Event Created.
Only the authenticated user's token is used; supervisor must approve before execution.
"""

import logging
import re
from datetime import datetime, timezone, timedelta

from tools import book_rapido, schedule_meal
from .tool_execution import run_tool_execution

logger = logging.getLogger(__name__)

# Default time window for derived "Student plan" event (UTC)
_DEFAULT_START_HOUR = 8
_DEFAULT_START_MINUTE = 0
_DEFAULT_DURATION_HOURS = 4


def _parse_wake_time(wake_time: str | None) -> tuple[int, int]:
    """Parse wake_time string (e.g. '8:00', '08:30') to (hour, minute)."""
    if not wake_time or not isinstance(wake_time, str):
        return _DEFAULT_START_HOUR, _DEFAULT_START_MINUTE
    wake_time = wake_time.strip()
    # Match HH:MM or H:MM
    m = re.match(r"^(\d{1,2}):(\d{2})$", wake_time)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return h, mi
    return _DEFAULT_START_HOUR, _DEFAULT_START_MINUTE


def derive_calendar_events_from_plan(
    decision: dict,
    profile: dict | None = None,
    tz: timezone = timezone.utc,
) -> list[dict]:
    """
    Derive one or more structured calendar events from the Supervisor's plan.

    Used when confidence >= threshold to feed the Tool Execution Agent.
    Produces at least one "Student plan" event with today's date and
    start/end from profile wake_time or defaults.
    """
    today = datetime.now(tz=tz).date()
    hour, minute = _parse_wake_time(profile.get("wake_time") if profile else None)
    start_dt = datetime(
        today.year, today.month, today.day, hour, minute, 0, tzinfo=tz
    )
    end_dt = start_dt + timedelta(hours=_DEFAULT_DURATION_HOURS)

    # ISO 8601 for the tool (Z suffix for UTC)
    def to_iso(d: datetime) -> str:
        if d.tzinfo == timezone.utc or d.utcoffset() == timedelta(0):
            return d.strftime("%Y-%m-%dT%H:%M:%SZ")
        off = d.utcoffset() or timedelta(0)
        sign = "+" if off >= timedelta(0) else "-"
        h, r = divmod(abs(off.total_seconds()), 3600)
        m, _ = divmod(r, 60)
        return d.strftime("%Y-%m-%dT%H:%M:%S") + f"{sign}{int(h):02d}:{int(m):02d}"
    start_iso = to_iso(start_dt)
    end_iso = to_iso(end_dt)

    parts = [
        decision.get("reasoning", ""),
        f"Priorities: {decision.get('priority', '')}",
        f"Route: {decision.get('route', '')}",
        f"Meal: {decision.get('meal', '')}",
    ]
    description = "\n".join(p for p in parts if p)

    return [
        {
            "title": "Student plan",
            "start_time": start_iso,
            "end_time": end_iso,
            "description": description.strip() or "Morning plan from Student Life Planner",
        }
    ]


def execute_plan(plan: dict, user_id: str | None = None):
    """
    Execute plan: ride booking and meal scheduling (existing behaviour).
    Does NOT run Google Calendar; that is gated by confidence in the Supervisor.
    """
    route = plan.get("route", "")
    meal = plan.get("meal", "")

    ride_result = None
    if route and ("bike" in route.lower() or "rapido" in route.lower()):
        ride_result = book_rapido(route)

    meal_result = schedule_meal(meal)

    return {
        "ride": ride_result,
        "meal": meal_result,
        "execution_status": "completed",
        "calendar": None,  # Set by Supervisor when confidence >= threshold
    }


def _fetch_access_token(user_id: str | None) -> str | None:
    """
    Fetch the user's Google OAuth access_token from Supabase.
    Tries user_profile.access_token first, then oauth_tokens. Ensures token
    belongs to the current user (only fetch by user_id).
    """
    if not user_id:
        return None
    try:
        from db import supabase
        # Prefer user_profile.access_token (if column exists)
        r = supabase.table("user_profile").select("access_token").eq("id", user_id).limit(1).execute()
        if r.data and len(r.data) > 0 and r.data[0].get("access_token"):
            return r.data[0]["access_token"].strip()
        # Fallback: oauth_tokens for this user
        r = supabase.table("oauth_tokens").select("access_token").eq("id", user_id).eq("provider", "google").limit(1).execute()
        if r.data and len(r.data) > 0 and r.data[0].get("access_token"):
            return r.data[0]["access_token"].strip()
    except Exception as e:
        logger.warning("Could not fetch access_token for user_id=%s: %s", user_id, e)
    return None


def _log_execution(user_id: str, event_title: str, start_time: str, end_time: str) -> None:
    """Store executed event in execution_logs (user_id, event_title, start_time, end_time, created_at)."""
    if not user_id:
        return
    try:
        from db import supabase
        supabase.table("execution_logs").insert({
            "user_id": user_id,
            "event_title": event_title,
            "start_time": start_time,
            "end_time": end_time,
        }).execute()
    except Exception as e:
        logger.warning("Could not write execution_logs: %s", e)


def execute_calendar_if_confident(
    decision: dict,
    profile: dict | None,
    user_id: str | None,
    threshold: float,
) -> dict | None:
    """
    If decision confidence >= threshold, get approved events (from decision["events"] or derived),
    fetch the user's access_token from Supabase, then create events via calendar_service.
    Logs each created event to execution_logs. Returns { status: "success", events_created: N }.
    Falls back to run_tool_execution (oauth_tokens/refresh) if no access_token available.
    """
    if decision.get("confidence", 0) < threshold:
        return None
    # Events: supervisor output format { "events": [ { title, start_time, end_time } ] } or derive from plan
    events = decision.get("events") or derive_calendar_events_from_plan(decision, profile=profile)
    if not events:
        return None

    access_token = _fetch_access_token(user_id)
    if access_token:
        # Use calendar_service (access_token path); only authenticated user's token
        import calendar_service
        created = 0
        results = []
        for ev in events:
            title = (ev.get("title") or "Event").strip()
            start_time = (ev.get("start_time") or "").strip()
            end_time = (ev.get("end_time") or "").strip()
            if not start_time or not end_time:
                continue
            link = calendar_service.create_calendar_event(
                access_token, title, start_time, end_time
            )
            if link:
                created += 1
                _log_execution(user_id, title, start_time, end_time)
                results.append({"title": title, "html_link": link})
        return {
            "status": "success",
            "events_created": created,
            "results": results,
            "execution_status": "completed",
            "tool": "google_calendar",
        }

    # No access_token: use existing Tool Execution Agent (oauth_tokens / refresh token)
    out = run_tool_execution(events, user_id=user_id)
    created = out.get("success_count", 0)
    if user_id and created:
        for r in out.get("results") or []:
            if r.get("success") and r.get("title"):
                _log_execution(
                    user_id,
                    r["title"],
                    r.get("start_time", ""),
                    r.get("end_time", ""),
                )
    out["status"] = "success"
    out["events_created"] = created
    return out
