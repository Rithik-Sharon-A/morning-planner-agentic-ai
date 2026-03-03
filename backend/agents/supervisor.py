import os
import logging
from dotenv import load_dotenv
from .crewai_agents import MemoryContext, run_crew
from .execution import execute_plan, execute_calendar_if_confident

load_dotenv()
logger = logging.getLogger(__name__)


class SupervisorAgent:
    def get_decision(self, profile: dict = None, events: list = None, user_id: str = None):
        try:
            memory_context = self._build_memory_context(profile=profile, events=events, user_id=user_id)
            logger.info("[memory] MemoryContext personal_memory count=%s", len(memory_context.get("personal_memory") or []))
            crew_result    = run_crew(memory_context, user_id=user_id)
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
                "models": {
                    "preference": os.getenv("PREFERENCE_MODEL", ""),
                    "logistics":  os.getenv("LOGISTICS_MODEL", ""),
                    "schedule":   os.getenv("SCHEDULE_MODEL", ""),
                },
            }

            execution_result = execute_plan(
                {"route": logistics_out, "meal": preference_out},
                user_id=user_id,
            )
            threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
            # Only trigger Tool Execution Agent (Google Calendar) when confidence >= threshold
            calendar_result = execute_calendar_if_confident(
                decision, profile=profile, user_id=user_id, threshold=threshold
            )
            if calendar_result is not None:
                execution_result["calendar"] = calendar_result
            decision["execution"] = execution_result

            if decision["confidence"] < threshold:
                decision["needs_human"] = True

            return decision

        except Exception as e:
            return self._fallback(str(e))

    def _build_memory_context(self, profile: dict = None, events: list = None, user_id: str = None) -> MemoryContext:
        """Build MemoryContext: profile, personal_memory (from Supabase), events. All agents receive this."""
        personal_memory: list = []
        if user_id:
            try:
                from memory.simple_memory import retrieve_all_memories_asc
                personal_memory = retrieve_all_memories_asc(user_id)
                logger.info("[memory] fetched personal_memory for user_id=%s count=%s", user_id, len(personal_memory))
            except Exception as e:
                logger.warning("[memory] fetch failed for user_id=%s: %s", user_id, e)
        return {
            "profile": profile or {},
            "personal_memory": personal_memory,
            "events": events or [],
        }

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
            "models": {"preference": "", "logistics": "", "schedule": ""},
            "execution": None,
            "needs_human": True,
        }
