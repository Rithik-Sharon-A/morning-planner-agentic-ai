# Prefer LiteLLM from short path (avoids Windows long-path error when installed in venv)
import sys
_site = getattr(sys, "litellm_site", r"C:\litellm_site")
if _site not in sys.path:
    sys.path.insert(0, _site)

import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from db import supabase
from agents.supervisor import SupervisorAgent
from agents.tool_execution import run_tool_execution
from memory.simple_memory import add_memory

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────
class UserProfileIn(BaseModel):
    user_id: str | None = None  # optional; when provided, profile is stored under this id (frontend UUID)
    diet: str
    commute_mode: str
    wake_time: str
    focus_goal: str

class EventIn(BaseModel):
    user_id: str
    event_text: str

class MemoryIn(BaseModel):
    user_id: str
    content: str


class CalendarEventIn(BaseModel):
    """Structured input for one calendar event (ISO 8601 datetimes)."""
    title: str
    start_time: str
    end_time: str
    description: str = ""


class ExecuteCalendarEventsIn(BaseModel):
    """Request body for Tool Execution Agent (calendar only)."""
    user_id: str | None = None
    events: list[CalendarEventIn]


# ── Endpoints ─────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "Morning Agent Running"}


@app.get("/models")
def get_models():
    return {
        "schedule_model": os.getenv("SCHEDULE_MODEL"),
        "logistics_model": os.getenv("LOGISTICS_MODEL"),
        "preference_model": os.getenv("PREFERENCE_MODEL"),
        "supervisor_model": os.getenv("SUPERVISOR_MODEL"),
    }


@app.post("/create-user")
async def create_user(body: UserProfileIn):
    try:
        row = {
            "diet":         body.diet,
            "commute_mode": body.commute_mode,
            "wake_time":    body.wake_time,
            "focus_goal":   body.focus_goal,
        }
        if body.user_id:
            row["id"] = body.user_id
            res = supabase.table("user_profile").upsert(row, on_conflict="id").execute()
        else:
            res = supabase.table("user_profile").insert(row).execute()
        user_id = res.data[0]["id"]
        logger.info(f"POST /create-user user_id={user_id}")
        return {"user_id": user_id}
    except Exception as e:
        logger.exception("Error creating user")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-event")
async def add_event(body: EventIn):
    try:
        supabase.table("daily_events").insert({
            "user_id":    body.user_id,
            "event_text": body.event_text,
        }).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-memory")
async def add_memory_endpoint(body: MemoryIn):
    try:
        success = add_memory(body.user_id, body.content)
        if success:
            logger.info(f"POST /add-memory user_id={body.user_id}")
            return {"status": "ok"}
        raise HTTPException(status_code=500, detail="Failed to add memory")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-profile")
async def get_profile(user_id: str = Query(...)):
    try:
        res = supabase.table("user_profile").select("*").eq("id", user_id).execute()
        if not res.data:
            return None  # 200 + null so frontend can clear stale user_id
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plans")
async def get_plans(user_id: str = Query(...)):
    try:
        res = supabase.table("generated_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(3).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/morning-plan")
async def morning_plan(user_id: str = Query(default=None)):
    try:
        logger.info(f"GET /morning-plan user_id={user_id}")
        profile = None
        events = []

        if user_id:
            # Fetch user profile
            p = supabase.table("user_profile").select("*").eq("id", user_id).execute()
            profile = p.data[0] if p.data else None

            # Fetch today's events
            e = supabase.table("daily_events").select("*").eq("user_id", user_id).execute()
            events = [row["event_text"] for row in e.data] if e.data else []

        supervisor = SupervisorAgent()
        decision = supervisor.get_decision(profile=profile, events=events, user_id=user_id)

        # Store generated plan
        if user_id:
            supabase.table("generated_plans").insert({
                "user_id": user_id,
                "plan":    decision,
            }).execute()

        return decision

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-calendar-events")
async def execute_calendar_events(body: ExecuteCalendarEventsIn):
    """
    Trigger the LangChain Tool Execution Agent to write events to Google Calendar.

    Only the Supervisor (or an authorised orchestrator) should use this when
    confidence >= threshold. Accepts structured events with ISO 8601 datetimes.
    """
    try:
        if not body.events:
            return {
                "execution_status": "completed",
                "tool": "google_calendar",
                "total_events": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "errors": [],
            }
        events = [
            {
                "title": e.title,
                "start_time": e.start_time,
                "end_time": e.end_time,
                "description": e.description or "",
            }
            for e in body.events
        ]
        result = run_tool_execution(events, user_id=body.user_id)
        logger.info(
            "POST /execute-calendar-events user_id=%s success=%s failure=%s",
            body.user_id,
            result.get("success_count", 0),
            result.get("failure_count", 0),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Tool execution failed")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
