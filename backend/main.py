from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from db import supabase
from agents.supervisor import SupervisorAgent

load_dotenv()

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
    diet: str
    commute_mode: str
    wake_time: str
    focus_goal: str

class EventIn(BaseModel):
    user_id: str
    event_text: str


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
        res = supabase.table("user_profile").insert({
            "diet":         body.diet,
            "commute_mode": body.commute_mode,
            "wake_time":    body.wake_time,
            "focus_goal":   body.focus_goal,
        }).execute()
        user_id = res.data[0]["id"]
        return {"user_id": user_id}
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()
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
        decision = supervisor.get_decision(profile=profile, events=events)

        # Store generated plan
        if user_id:
            supabase.table("generated_plans").insert({
                "user_id": user_id,
                "plan":    decision,
            }).execute()

        threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        if decision["confidence"] < threshold:
            decision["needs_human"] = True

        return decision

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
