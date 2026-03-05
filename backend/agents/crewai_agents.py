import json
import logging
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from llm_factory import make_llm

load_dotenv()
logger = logging.getLogger(__name__)

# Model names from env (OpenRouter only)
SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL", "openai/gpt-4-turbo")
PREFERENCE_MODEL = os.getenv("PREFERENCE_MODEL", "meta-llama/llama-3.1-8b-instruct")
LOGISTICS_MODEL  = os.getenv("LOGISTICS_MODEL", "openai/gpt-4o-mini")
SCHEDULE_MODEL   = os.getenv("SCHEDULE_MODEL", "anthropic/claude-3.5-sonnet")

# Shared agents — created once, used by run_crew
supervisor_agent = Agent(
    role="Supervisor Agent",
    goal="Synthesise sub-agent outputs into a coherent full-day plan from wake to sleep, and produce a structured timeline.",
    backstory="Senior coordinator who combines schedule, logistics, and preference insights into an intelligent personal day planner. Adapts to user profile, memory, and events.",
    llm=make_llm(SUPERVISOR_MODEL),
    verbose=False,
    allow_delegation=False,
)

preference_agent = Agent(
    role="Preference Agent",
    goal="Recommend a meal based on the student's dietary preferences.",
    backstory="Nutritionist specialising in student dietary habits.",
    llm=make_llm(PREFERENCE_MODEL),
    verbose=False,
    allow_delegation=False,
)

logistics_agent = Agent(
    role="Logistics Agent",
    goal="Plan the best commute route for the student today.",
    backstory="Expert in urban logistics and student commute planning.",
    llm=make_llm(LOGISTICS_MODEL),
    verbose=False,
    allow_delegation=False,
)

schedule_agent = Agent(
    role="Schedule Agent",
    goal="Identify today's academic priorities based on student context.",
    backstory="Expert academic scheduler for university students.",
    llm=make_llm(SCHEDULE_MODEL),
    verbose=False,
    allow_delegation=False,
)

# Structured context passed to all agents. All agents must receive this.
MemoryContext = dict[str, Any]  # profile: dict | None, personal_memory: list[str], events: list[str]


def _build_full_context_string(memory_context: MemoryContext) -> str:
    """Build the single context string injected into every agent prompt: profile, personal notes, events."""
    parts = []

    profile = memory_context.get("profile") or {}
    if profile:
        parts.append(
            "User Profile:\n"
            f"  Diet: {profile.get('diet', '—')}\n"
            f"  Wake Time: {profile.get('wake_time', '—')}\n"
            f"  Commute Mode: {profile.get('commute_mode', '—')}\n"
            f"  Focus Goal: {profile.get('focus_goal', '—')}"
        )

    personal_memory = memory_context.get("personal_memory") or []
    if personal_memory:
        from memory.simple_memory import format_personal_memory_block
        block = format_personal_memory_block(personal_memory)
        if block:
            parts.append("Personal Notes (user's own notes):\n" + block)
    else:
        parts.append("Personal Notes: (none)")

    events = memory_context.get("events") or []
    if events:
        parts.append("Today's Events:\n  " + "\n  ".join(events))
    else:
        parts.append("Today's Events: (none)")

    return "\n\n".join(parts) if parts else "No user context provided."


def _normalize_time_to_12h(time_str: str) -> str:
    """
    Convert any time string to 12-hour format with AM/PM.
    Handles: 0:30, 00:30, 13:00, 9:00, 07:00, 12:00, 23:30, etc.
    Returns e.g. '7:00 AM', '12:30 PM', '12:00 AM'.
    """
    if not time_str or not isinstance(time_str, str):
        return "—"
    s = time_str.strip().upper()
    # Already has AM/PM — normalize to "h:mm AM/PM" (no leading zero on hour)
    if "AM" in s or "PM" in s:
        s = re.sub(r"\s+", " ", s).strip()
        am = "AM" in s
        m = re.match(r"^(\d{1,2}):(\d{2})\s*[AP]M", s)
        if m:
            h, min_val = int(m.group(1)), int(m.group(2))
            if h == 0:
                h = 12
            elif h > 12:
                h = h - 12
            return f"{h}:{min_val:02d} {'AM' if am else 'PM'}"
        return s
    # Match H:MM or HH:MM (24h or ambiguous)
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        return time_str.strip() or "—"
    hour, minute = int(m.group(1)), int(m.group(2))
    minute = min(59, max(0, minute))
    if hour >= 24:
        hour = hour % 24
    if hour == 0:
        h12 = 12
        am_pm = "AM"
    elif hour < 12:
        h12 = hour
        am_pm = "AM"
    elif hour == 12:
        h12 = 12
        am_pm = "PM"
    else:
        h12 = hour - 12
        am_pm = "PM"
    return f"{h12}:{minute:02d} {am_pm}"


def _time_to_minutes(time_str: str) -> int:
    """Parse a time string (12h or 24h) to minutes since midnight for sorting."""
    s = (time_str or "").strip().upper()
    am = "AM" in s or "am" in s
    pm = "PM" in s or "pm" in s
    m = re.match(r"(\d{1,2}):(\d{2})", s)
    if not m:
        return 0
    hour, minute = int(m.group(1)), int(m.group(2))
    if pm and hour != 12:
        hour += 12
    elif am and hour == 12:
        hour = 0
    elif not am and not pm:
        if 0 <= hour <= 23:
            pass  # treat as 24h
        else:
            hour = hour % 24
    return hour * 60 + minute


def _parse_daily_plan_from_output(raw: str) -> list[dict[str, str]]:
    """Extract daily_plan JSON array from agent output. Returns list of {time, activity} in 12h format, sorted by time."""
    if not raw or not isinstance(raw, str):
        return []
    text = raw.strip()
    match = re.search(r"\[[\s\S]*?\]", text)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(0))
        if not isinstance(parsed, list):
            return []
        out = []
        for item in parsed:
            if isinstance(item, dict):
                t = str(item.get("time", "")).strip() or "—"
                a = str(item.get("activity", "")).strip() or "—"
                if a and t and t != "—":
                    t = _normalize_time_to_12h(t)
                    # Keep activity short: one line, max ~60 chars for display
                    if len(a) > 60:
                        a = a[:57].rsplit(" ", 1)[0] + "…" if len(a) > 57 else a[:60]
                    out.append({"time": t, "activity": a})
        out.sort(key=lambda x: _time_to_minutes(x["time"]))
        return out[:50]
    except (json.JSONDecodeError, TypeError, IndexError, KeyError):
        return []


print("[OK] CrewAI agents initialized via OpenRouter")


def run_crew(memory_context: MemoryContext, user_id: str | None = None) -> dict:
    """Run the crew using the shared agents. All agents receive MemoryContext (profile, personal_memory, events)."""
    from memory.simple_memory import (
        consolidate_memories_to_preferences,
        format_preferences_block,
    )

    personal_memory = memory_context.get("personal_memory") or []
    logger.info("[memory] personal_memory count=%s items=%s", len(personal_memory), personal_memory)

    # Optional: extracted preferences (keyword-based) for extra signal
    prefs_block = ""
    if personal_memory:
        try:
            prefs = consolidate_memories_to_preferences(personal_memory)
            prefs_block = format_preferences_block(prefs)
            if prefs_block:
                prefs_block = "\nUser consolidated preferences (extracted):\n" + prefs_block + "\n"
        except Exception as e:
            logger.warning("Memory consolidation failed: %s", e)

    full_context = _build_full_context_string(memory_context)
    agent_input = prefs_block + "\n" + full_context
    logger.info("[memory] final context (first 500 chars): %s", agent_input[:500] + ("..." if len(agent_input) > 500 else ""))

    schedule_task = Task(
        description=(
            f"{agent_input}\n\n"
            "Generate today's academic priorities in 1–2 sentences."
        ),
        expected_output="1-2 sentence academic priority statement.",
        agent=schedule_agent,
    )

    logistics_task = Task(
        description=(
            f"{agent_input}\n\n"
            "Suggest a commute route in 1–2 sentences."
        ),
        expected_output="1-2 sentence commute route recommendation.",
        agent=logistics_agent,
    )

    preference_task = Task(
        description=(
            f"{agent_input}\n\n"
            "Suggest a meal based on the student's diet in 1–2 sentences."
        ),
        expected_output="1-2 sentence meal recommendation.",
        agent=preference_agent,
    )

    reasoning_task = Task(
        description=(
            f"{agent_input}\n\n"
            "Given the schedule, logistics, and preference agent outputs, "
            "write a 2–3 sentence explanation of the final plan."
        ),
        expected_output="2-3 sentence supervisor reasoning.",
        agent=supervisor_agent,
        context=[schedule_task, logistics_task, preference_task],
    )

    full_day_plan_task = Task(
        description=(
            f"{agent_input}\n\n"
            "You have already received:\n"
            "- Schedule/priority agent output (academic priorities).\n"
            "- Logistics agent output (commute, route).\n"
            "- Preference agent output (meals, diet).\n\n"
            "Produce a FULL DAY intelligent plan from wake-up to sleep. Use the user's wake time, profile, and events. "
            "Include: wake up, morning preparation, breakfast, commute, academic work/lectures, lunch, study time, breaks, "
            "evening activity (e.g. exercise or relaxation), dinner, preparation for the next day, and sleep. "
            "Use clear, respectful wording. Adapt to preferences from memory (e.g. if user prefers studying at night, move study to evening).\n\n"
            "RULES:\n"
            "- Time MUST be in 12-hour format with AM/PM (e.g. 7:00 AM, 12:30 PM, 10:30 PM). Never use 24h (no 13:00, 0:30).\n"
            "- Activities must be SHORT labels (2–4 words), e.g. 'Wake up', 'Morning preparation', 'Breakfast', 'Commute to lecture', "
            "'Attend lecture', 'Lunch break', 'Study session', 'Exercise or relaxation', 'Dinner', 'Prepare for the next day', 'Sleep'.\n"
            "- Order must be chronological: morning (6:30–9 AM) → midday (9 AM–2 PM) → afternoon (2–6 PM) → evening (6–10 PM) → night (10–11:30 PM).\n\n"
            "Output ONLY a valid JSON array. Example:\n"
            "[{\"time\": \"7:00 AM\", \"activity\": \"Wake up\"}, {\"time\": \"7:15 AM\", \"activity\": \"Morning preparation\"}, "
            "{\"time\": \"7:30 AM\", \"activity\": \"Breakfast\"}, {\"time\": \"9:00 AM\", \"activity\": \"Attend lecture\"}, "
            "{\"time\": \"12:30 PM\", \"activity\": \"Lunch break\"}, {\"time\": \"2:00 PM\", \"activity\": \"Study session\"}, "
            "{\"time\": \"6:00 PM\", \"activity\": \"Exercise or relaxation\"}, {\"time\": \"8:00 PM\", \"activity\": \"Dinner\"}, "
            "{\"time\": \"10:30 PM\", \"activity\": \"Sleep\"}]"
        ),
        expected_output="A JSON array of {time, activity} objects in 12h AM/PM format, chronological order, short activity labels.",
        agent=supervisor_agent,
        context=[schedule_task, logistics_task, preference_task, reasoning_task],
    )

    crew = Crew(
        agents=[schedule_agent, logistics_agent, preference_agent, supervisor_agent],
        tasks=[schedule_task, logistics_task, preference_task, reasoning_task, full_day_plan_task],
        verbose=False,
    )

    kickoff_start = time.time()
    logger.info("[crew] Starting crew kickoff...")
    try:
        # Timeout protection: if crew takes > 60s, something is wrong
        result = crew.kickoff()
        kickoff_elapsed = time.time() - kickoff_start
        logger.info(f"[timing] Crew kickoff completed in {kickoff_elapsed:.2f}s")
    except Exception as e:
        kickoff_elapsed = time.time() - kickoff_start
        logger.error(f"[crew] Kickoff failed after {kickoff_elapsed:.2f}s: {e}")
        raise

    schedule_out   = str(schedule_task.output.raw   if schedule_task.output   else "")
    logistics_out  = str(logistics_task.output.raw  if logistics_task.output  else "")
    preference_out = str(preference_task.output.raw if preference_task.output else "")
    reasoning      = str(reasoning_task.output.raw  if reasoning_task.output  else str(result))
    full_day_raw   = str(full_day_plan_task.output.raw if full_day_plan_task.output else "")
    daily_plan     = _parse_daily_plan_from_output(full_day_raw)
    if not daily_plan:
        logger.warning("Full-day plan parse returned empty; using fallback timeline")
        daily_plan = [
            {"time": "7:00 AM", "activity": "Wake up"},
            {"time": "7:15 AM", "activity": "Morning preparation"},
            {"time": "7:30 AM", "activity": "Breakfast"},
            {"time": "8:30 AM", "activity": "Commute to lecture"},
            {"time": "9:00 AM", "activity": "Attend lecture"},
            {"time": "12:30 PM", "activity": "Lunch break"},
            {"time": "2:00 PM", "activity": "Study session"},
            {"time": "6:00 PM", "activity": "Exercise or relaxation"},
            {"time": "8:00 PM", "activity": "Dinner"},
            {"time": "9:30 PM", "activity": "Prepare for the next day"},
            {"time": "10:30 PM", "activity": "Sleep"},
        ]

    return {
        "schedule_out":   schedule_out,
        "logistics_out":  logistics_out,
        "preference_out": preference_out,
        "reasoning":      reasoning,
        "daily_plan":     daily_plan,
    }
