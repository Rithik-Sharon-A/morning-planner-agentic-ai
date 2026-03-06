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
from task_service import get_user_tasks, complete_task

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




# ── Endpoints ─────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "Morning Agent Running"}




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
        # Remove access_token from response (no longer used)
        row.pop("access_token", None)
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


@app.get("/tasks")
async def get_tasks(user_id: str = Query(...), status: str = Query(default=None)):
    """
    Fetch AI-generated tasks for a user from Supabase ai_tasks table.
    
    Query params:
        user_id: User ID (required)
        status: Optional status filter ('pending', 'completed', 'cancelled')
    """
    try:
        tasks = get_user_tasks(user_id, status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/tasks/{task_id}/complete")
async def complete_task_endpoint(task_id: str, user_id: str = Query(...)):
    """
    Mark a task as completed.
    
    Path params:
        task_id: Task UUID
    Query params:
        user_id: User ID (for security verification)
    """
    try:
        result = complete_task(task_id, user_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/morning-plan")
async def morning_plan(
    user_id: str = Query(default=None),
    current_time: str = Query(default=None),
    current_date: str = Query(default=None),
    day_of_week: str = Query(default=None)
):
    try:
        logger.info(f"GET /morning-plan user_id={user_id} current_time={current_time}")
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
        decision = supervisor.get_decision(
            profile=profile, 
            events=events, 
            user_id=user_id,
            current_time=current_time,
            current_date=current_date,
            day_of_week=day_of_week
        )

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
        supabase.table("ai_tasks").delete().eq("user_id", user_id).execute()
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




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
