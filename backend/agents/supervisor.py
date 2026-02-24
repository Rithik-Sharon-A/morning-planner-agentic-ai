import os
import logging
from dotenv import load_dotenv
from .crewai_agents import (
    run_crew,
    supervisor_agent,
    preference_agent,
    logistics_agent,
    schedule_agent,
)
from .execution import execute_plan

load_dotenv()
logger = logging.getLogger(__name__)


class SupervisorAgent:
    def get_decision(self, profile: dict = None, events: list = None, user_id: str = None):
        try:
            context = self._build_context(profile, events)
            
            enriched_context = context
            if user_id:
                try:
                    from memory.simple_memory import retrieve_memories
                    memories = retrieve_memories(user_id, limit=5)
                    if memories:
                        memory_lines = "\n".join(f"- {m}" for m in memories)
                        enriched_context = (
                            f"User past memories:\n{memory_lines}\n\n"
                            f"Current request:\n{context}"
                        )
                        logger.info(f"Past memories injected: {len(memories)}")
                except Exception as e:
                    logger.warning(f"Memory retrieval failed, continuing without: {e}")

            crew_result    = run_crew(enriched_context)
            schedule_out   = crew_result["schedule_out"]
            logistics_out  = crew_result["logistics_out"]
            preference_out = crew_result["preference_out"]
            reasoning      = crew_result["reasoning"]

            decision = {
                "meal":       preference_out,
                "route":      logistics_out,
                "priority":   schedule_out,
                "confidence": 0.75,
                "reasoning":  reasoning,
                "agent_logs": {
                    "schedule":   schedule_out,
                    "logistics":  logistics_out,
                    "preference": preference_out,
                },
            }

            execution_result = execute_plan({
                "route": logistics_out,
                "meal":  preference_out,
            })
            decision["execution"] = execution_result

            threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
            if decision["confidence"] < threshold:
                decision["needs_human"] = True

            return decision

        except Exception as e:
            return self._fallback(str(e))

    def _build_context(self, profile: dict, events: list) -> str:
        parts = []
        if profile:
            parts.append(
                f"User profile — diet: {profile.get('diet')}, "
                f"commute: {profile.get('commute_mode')}, "
                f"wake time: {profile.get('wake_time')}, "
                f"focus goal: {profile.get('focus_goal')}."
            )
        if events:
            parts.append(f"Today's events: {', '.join(events)}.")
        return " ".join(parts) if parts else "No user context provided."

    def _fallback(self, error=""):
        return {
            "meal":       "Unable to fetch meal recommendation",
            "route":      "Unable to fetch route",
            "priority":   "Unable to fetch priorities",
            "confidence": 0.0,
            "reasoning":  f"Agent failed to respond. Error: {error}",
            "agent_logs": {
                "schedule":   "Agent unavailable",
                "logistics":  "Agent unavailable",
                "preference": "Agent unavailable",
            },
            "execution": None,
        }
