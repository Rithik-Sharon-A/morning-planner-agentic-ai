import os
import logging
import time
from dotenv import load_dotenv
from .crewai_agents import MemoryContext, run_crew
from .execution import execute_plan, execute_calendar_if_confident

load_dotenv()
logger = logging.getLogger(__name__)


class SupervisorAgent:
    def get_decision(
        self, 
        profile: dict = None, 
        events: list = None, 
        user_id: str = None,
        current_time: str = None,
        current_date: str = None,
        day_of_week: str = None
    ):
        start_time = time.time()
        try:
            logger.info(f"[supervisor] Starting decision for user_id={user_id} current_time={current_time}")
            memory_context = self._build_memory_context(
                profile=profile, 
                events=events, 
                user_id=user_id,
                current_time=current_time,
                current_date=current_date,
                day_of_week=day_of_week
            )
            logger.info("[memory] MemoryContext personal_memory count=%s", len(memory_context.get("personal_memory") or []))
            
            crew_start = time.time()
            crew_result    = run_crew(memory_context, user_id=user_id)
            crew_elapsed = time.time() - crew_start
            logger.info(f"[timing] Crew execution took {crew_elapsed:.2f}s")
            schedule_out   = crew_result["schedule_out"]
            logistics_out  = crew_result["logistics_out"]
            preference_out = crew_result["preference_out"]
            reasoning      = crew_result["reasoning"]
            daily_plan     = crew_result.get("daily_plan") or []

            confidence = 0.75
            threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))
            # Supervisor approval gate: if confidence > threshold, allow Execution Agent to run
            decision = {
                "meal":       preference_out,
                "route":      logistics_out,
                "priority":   schedule_out,
                "confidence": confidence,
                "confidence_score": confidence,  # alias for compatibility
                "reasoning":  reasoning,
                "daily_plan": daily_plan,
                "events": None,  # Execution layer derives or uses this when present
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
            
            # Supervisor approval gate: only trigger Execution Agent when confidence >= threshold
            # Guard: prevent duplicate execution
            if confidence >= threshold and not decision.get("execution_done"):
                # Auto-execute: save AI tasks to Supabase
                if daily_plan and user_id:
                    try:
                        task_start = time.time()
                        from task_service import save_ai_tasks
                        task_events = [{"title": item["activity"], "time": item["time"]} for item in daily_plan]
                        task_result = save_ai_tasks(user_id, task_events)
                        task_elapsed = time.time() - task_start
                        execution_result["tasks"] = task_result
                        decision["execution_done"] = True  # Mark as executed to prevent re-execution
                        logger.info(f"[tasks] Auto-executed for user_id={user_id}, created={task_result.get('tasks_created', 0)}, took {task_elapsed:.2f}s")
                    except Exception as e:
                        logger.exception(f"[tasks] Auto-execution failed: {e}")
                        execution_result["tasks"] = {"status": "error", "message": str(e), "tasks_created": 0}
            else:
                decision["needs_human"] = True  # request user confirmation
            
            decision["execution"] = execution_result

            if decision["confidence"] < threshold:
                decision["needs_human"] = True

            total_elapsed = time.time() - start_time
            logger.info(f"[timing] Total supervisor decision took {total_elapsed:.2f}s")
            return decision

        except Exception as e:
            return self._fallback(str(e))

    def _build_memory_context(
        self, 
        profile: dict = None, 
        events: list = None, 
        user_id: str = None,
        current_time: str = None,
        current_date: str = None,
        day_of_week: str = None
    ) -> MemoryContext:
        """Build MemoryContext: profile, personal_memory (from Supabase), events, and browser time. All agents receive this."""
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
            "current_time": current_time,
            "current_date": current_date,
            "day_of_week": day_of_week,
        }

    def _fallback(self, error=""):
        return {
            "meal":       "Unable to fetch meal recommendation",
            "route":      "Unable to fetch route",
            "priority":   "Unable to fetch priorities",
            "confidence": 0.0,
            "confidence_score": 0.0,
            "reasoning":  f"Agent failed to respond. Error: {error}",
            "daily_plan": [],
            "events": [],
            "agent_logs": {
                "schedule":   "Agent unavailable",
                "logistics":  "Agent unavailable",
                "preference": "Agent unavailable",
            },
            "models": {"preference": "", "logistics": "", "schedule": ""},
            "execution": None,
            "needs_human": True,
        }
