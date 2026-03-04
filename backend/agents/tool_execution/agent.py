"""
LangChain-based Tool Execution Agent.

Invoked only by the Supervisor when confidence >= threshold. Executes tools
(e.g. Google Calendar) with structured input. No reasoning agents call this;
tool execution is separate from schedule/logistics/preference reasoning.
"""

import logging
from typing import Any

from .tools.google_calendar import (
    CalendarEventInput,
    CalendarEventResult,
    create_calendar_event,
    create_calendar_event_tool,
)

logger = logging.getLogger(__name__)


class ToolExecutionAgent:
    """
    Agent that owns and runs tools (e.g. Google Calendar). No LLM in the
    execution path when given structured events; runs tools directly for
    deterministic, production-ready behaviour.
    """

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id
        self._calendar_tool = create_calendar_event_tool(user_id=user_id)

    def get_tools(self):
        """Return LangChain tools available to this agent."""
        return [self._calendar_tool]

    def run_calendar_events(
        self,
        events: list[dict[str, Any] | CalendarEventInput],
    ) -> dict[str, Any]:
        """
        Execute calendar event creation for a list of structured events.

        Validates and runs each event through the Google Calendar tool.
        Returns aggregated structured result (success count, results, errors).
        """
        results: list[CalendarEventResult] = []
        for i, ev in enumerate(events):
            if isinstance(ev, CalendarEventInput):
                inp = ev
            else:
                try:
                    inp = CalendarEventInput(
                        title=ev.get("title", ""),
                        start_time=ev.get("start_time", ""),
                        end_time=ev.get("end_time", ""),
                        description=ev.get("description", ""),
                    )
                except Exception as e:
                    results.append(
                        CalendarEventResult(
                            success=False,
                            error=f"Invalid event input: {e}",
                            title=ev.get("title", ""),
                            start_time=ev.get("start_time", ""),
                            end_time=ev.get("end_time", ""),
                        )
                    )
                    continue
            r = create_calendar_event(
                title=inp.title,
                start_time=inp.start_time,
                end_time=inp.end_time,
                description=inp.description,
                user_id=self.user_id,
            )
            results.append(r)

        success_count = sum(1 for r in results if r.success)
        failed = [r for r in results if not r.success]

        return {
            "execution_status": "completed",
            "tool": "google_calendar",
            "total_events": len(events),
            "success_count": success_count,
            "failure_count": len(failed),
            "results": [
                {
                    "success": r.success,
                    "event_id": r.event_id,
                    "html_link": r.html_link,
                    "error": r.error,
                    "title": r.title,
                    "start_time": r.start_time,
                    "end_time": r.end_time,
                }
                for r in results
            ],
            "errors": [r.error for r in failed if r.error],
        }


def run_tool_execution(
    events: list[dict[str, Any] | CalendarEventInput],
    user_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the Tool Execution Agent for the given structured calendar events.

    Only call this when Supervisor confidence >= threshold. This is the
    single entry point for tool execution from the Supervisor/orchestration layer.
    """
    agent = ToolExecutionAgent(user_id=user_id)
    return agent.run_calendar_events(events)
