"""
Tool Execution Agent package.

LangChain-based agent that executes tools (e.g. Google Calendar) only when
invoked by the Supervisor after confidence >= threshold. No reasoning agents
call tools directly.
"""

from .agent import ToolExecutionAgent, run_tool_execution
from .tools.google_calendar import create_calendar_event_tool

__all__ = [
    "ToolExecutionAgent",
    "run_tool_execution",
    "create_calendar_event_tool",
]
