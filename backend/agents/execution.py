"""
Execution layer: runs plans (ride, meal) and optionally the Tool Execution Agent
for Google Calendar when Supervisor confidence >= threshold.

No reasoning agent calls Google APIs directly; only this module invokes the
Tool Execution Agent.
"""

import os
import re
from datetime import datetime, timezone, timedelta

from tools import book_rapido, schedule_meal
from .tool_execution import run_tool_execution

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


def execute_calendar_if_confident(
    decision: dict,
    profile: dict | None,
    user_id: str | None,
    threshold: float,
) -> dict | None:
    """
    If decision confidence >= threshold, derive calendar events from the plan,
    run the Tool Execution Agent, and return the execution result. Otherwise
    return None. Only the Supervisor should call this.
    """
    if decision.get("confidence", 0) < threshold:
        return None
    events = derive_calendar_events_from_plan(decision, profile=profile)
    if not events:
        return None
    return run_tool_execution(events, user_id=user_id)
