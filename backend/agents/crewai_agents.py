import logging
import os
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
    goal="Synthesise sub-agent outputs into a coherent morning plan.",
    backstory="Senior coordinator who combines schedule, logistics, and preference insights.",
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
            "write a 2–3 sentence explanation of the final morning plan."
        ),
        expected_output="2-3 sentence supervisor reasoning.",
        agent=supervisor_agent,
        context=[schedule_task, logistics_task, preference_task],
    )

    crew = Crew(
        agents=[schedule_agent, logistics_agent, preference_agent, supervisor_agent],
        tasks=[schedule_task, logistics_task, preference_task, reasoning_task],
        verbose=False,
    )

    result = crew.kickoff()

    schedule_out   = str(schedule_task.output.raw   if schedule_task.output   else "")
    logistics_out  = str(logistics_task.output.raw  if logistics_task.output  else "")
    preference_out = str(preference_task.output.raw if preference_task.output else "")
    reasoning      = str(reasoning_task.output.raw  if reasoning_task.output  else str(result))

    return {
        "schedule_out":   schedule_out,
        "logistics_out":  logistics_out,
        "preference_out": preference_out,
        "reasoning":      reasoning,
    }
