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
from google_calendar_service import execute_daily_plan_to_calendar

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI()

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").strip().split(",")
_cors_origins = [o.strip() for o in _cors_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
    email: str | None = None  # optional; when provided (e.g. from Google auth), stored in user_profile.email

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


class AuthUserIn(BaseModel):
    """Payload sent by the frontend immediately after a successful Google OAuth login."""
    user_id: str
    email: str | None = None  # Google email; optional so null/omit never fails validation


class DailyPlanEvent(BaseModel):
    """Single event from daily plan timeline."""
    title: str
    time: str  # e.g. "7:00 AM" or "07:00"


class ExecuteCalendarPlanIn(BaseModel):
    """Request body for /api/execute-calendar-plan endpoint."""
    user_id: str
    events: list[DailyPlanEvent]


class StoreGoogleTokenIn(BaseModel):
    """Request body for POST /api/store-google-token. Frontend sends after user grants Calendar scope."""
    user_id: str
    access_token: str


# ── Endpoints ─────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "Morning Agent Running"}


@app.post("/api/store-google-token")
async def store_google_token(body: StoreGoogleTokenIn):
    """
    Store the user's Google OAuth access_token in Supabase user_profile.
    Frontend calls this after the user completes Google Calendar OAuth consent.
    Security: only the authenticated user's token is stored (user_id from Supabase session).
    """
    try:
        if not body.user_id or not body.user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        if not body.access_token or not body.access_token.strip():
            raise HTTPException(status_code=400, detail="access_token is required")

        user_id = body.user_id.strip()
        access_token = body.access_token.strip()

        # Update access_token for the authenticated user only (do not overwrite other columns).
        # Requires an existing user_profile row (created on login via upsert-auth-user).
        supabase.table("user_profile").update({"access_token": access_token}).eq("id", user_id).execute()

        logger.info(f"POST /api/store-google-token user_id={user_id} token stored")
        return {"status": "ok", "message": "Google token stored"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("store_google_token failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert-auth-user")
async def upsert_auth_user(body: AuthUserIn):
    """
    Called when the frontend has a Supabase Auth session (e.g. after Google login).
    - Gets user_id and email from the request (email comes from Supabase Auth / session).
    - Upserts into user_profile so the same email is stored in your Supabase DB table.
    """
    try:
        email = (body.email or "").strip()
        row = {"id": body.user_id, "email": email}
        supabase.table("user_profile").upsert(row, on_conflict="id").execute()
        if email:
            supabase.table("user_profile").update({"email": email}).eq("id", body.user_id).execute()
        logger.info(f"POST /upsert-auth-user user_id={body.user_id} email={email}")
        return {"user_id": body.user_id, "email": email, "status": "ok"}
    except Exception as e:
        logger.exception("Error upserting auth user")
        raise HTTPException(status_code=500, detail=str(e))


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
        if body.email is not None and str(body.email).strip():
            row["email"] = str(body.email).strip()
        if body.user_id:
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
        row = dict(res.data[0])
        # Do not expose access_token to frontend; expose only a boolean for UI state
        access_token = row.pop("access_token", None)
        row["calendar_connected"] = bool(access_token and str(access_token).strip())
        return row
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


@app.delete("/api/delete-user-data")
async def delete_user_data(user_id: str = Query(..., description="Authenticated user's id")):
    """
    Delete all data for the given user_id (query param). Frontend sends user_id in URL.
    Only the authenticated user should call this with their own user_id.
    Tables: user_profile, daily_events, generated_plans, user_memories; optional: schedule_history, agent_memory, execution_logs.
    """
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    user_id = user_id.strip()
    try:
        # Dependent tables first (by user_id), then profile (by id)
        supabase.table("daily_events").delete().eq("user_id", user_id).execute()
        supabase.table("generated_plans").delete().eq("user_id", user_id).execute()
        supabase.table("user_memories").delete().eq("user_id", user_id).execute()
        try:
            supabase.table("schedule_history").delete().eq("user_id", user_id).execute()
        except Exception:
            pass  # table may not exist
        try:
            supabase.table("agent_memory").delete().eq("user_id", user_id).execute()
        except Exception:
            pass  # table may not exist
        try:
            supabase.table("execution_logs").delete().eq("user_id", user_id).execute()
        except Exception:
            pass  # table may not exist
        try:
            supabase.table("oauth_tokens").delete().eq("id", user_id).execute()
        except Exception:
            pass  # table may not exist
        supabase.table("user_profile").delete().eq("id", user_id).execute()
        logger.info("DELETE /api/delete-user-data user_id=%s success", user_id)
        return {"status": "success"}
    except Exception as e:
        logger.exception("delete_user_data failed for user_id=%s", user_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-calendar-plan")
async def execute_calendar_plan(body: ExecuteCalendarPlanIn):
    """
    Execute daily plan by creating events in user's Google Calendar.
    
    Flow: User Request → Planning Agents → Supervisor Agent → Confidence Check → 
          Execution Agent → Google Calendar Tool → Events Created
    
    Only triggered when Supervisor confidence >= threshold (default 0.8).
    Fetches user's Google OAuth token from Supabase (security: only authenticated user's token).
    Creates events in primary calendar and logs to execution_logs.
    """
    try:
        if not body.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        if not body.events or len(body.events) == 0:
            return {
                "status": "success",
                "events_created": 0,
                "message": "No events to create"
            }
        
        # Convert Pydantic models to dicts for the service
        events_list = [{"title": e.title, "time": e.time} for e in body.events]
        
        # Execute via google_calendar_service (fetches token, creates events, logs)
        result = execute_daily_plan_to_calendar(body.user_id, events_list)
        
        logger.info(
            f"POST /api/execute-calendar-plan user_id={body.user_id} "
            f"events_created={result.get('events_created', 0)}"
        )
        
        return result
        
    except Exception as e:
        logger.exception("execute_calendar_plan failed")
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
