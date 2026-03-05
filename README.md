# AI Student Life Planner

A multi-agent AI system that generates optimized daily schedules and automatically executes approved plans by creating events in the user's Google Calendar. Individually designed and built as a production-grade agentic pipeline.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF6B6B)](https://www.crewai.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20DB-3ECF8E?logo=supabase)](https://supabase.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20Gateway-8320E6)](https://openrouter.ai/)
[![Google Calendar API](https://img.shields.io/badge/Google%20Calendar-API-4285F4?logo=google)](https://developers.google.com/calendar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Demo

Example of a generated full-day schedule (12-hour AM/PM format):

| Time     | Activity                  |
|----------|---------------------------|
| 7:00 AM  | Wake up                    |
| 7:15 AM  | Morning preparation        |
| 7:30 AM  | Breakfast                  |
| 8:30 AM  | Commute to lecture         |
| 9:00 AM  | Attend lecture             |
| 12:30 PM | Lunch break                |
| 2:00 PM  | Study session              |
| 6:00 PM  | Exercise or relaxation     |
| 8:00 PM  | Dinner                     |
| 9:30 PM  | Prepare for the next day   |
| 10:30 PM | Sleep                      |

Plans are derived from the user's profile (diet, wake time, commute mode, focus goal), personal memory, and daily events. When the supervisor's confidence score meets the threshold, events are created automatically in Google Calendar.

---

## Key Features

**Multi-Agent AI Architecture** — Supervisor coordinates four specialized agents (Schedule, Logistics, Preference, Execution) using CrewAI. Each agent can use a different LLM via OpenRouter for role-appropriate reasoning.

**Intelligent Daily Planning** — Full-day timeline from wake-up to sleep, adapted to profile and preferences. Output is chronological with short, clear activity labels in 12-hour AM/PM format.

**Google Calendar Automation** — Approved plans are written to the user's primary Google Calendar. OAuth 2.0 token is stored securely; execution runs only after a confidence check.

**Secure Authentication** — Google OAuth 2.0 via Supabase Auth. Session and user state are managed by Supabase; no credentials are hardcoded.

**Persistent User Memory** — Profiles, personal notes, and plan history live in Supabase. Context is injected into every agent run for consistent, personalized plans.

**Modern React UI** — Single-page app with Vite, Material-UI, and Framer Motion. Responsive layout, real-time pipeline feedback, and dark theme.

---

## Architecture

```
React Frontend (Vite + MUI)
         │
         ▼ HTTP/REST
FastAPI Backend
         │
         ▼
Supervisor Agent (confidence scoring, execution gate)
         │
         ▼
CrewAI Sub-Agents (Schedule | Logistics | Preference)
         │
         ▼
LLM Models via OpenRouter (GPT-4o-mini, Claude, Llama)
         │
         ▼
Supabase (Auth, profile, memory, plans)  +  Google Calendar API (events)
```

The frontend talks only to the FastAPI backend. The supervisor invokes the crew, aggregates outputs, computes confidence, and—when above threshold—triggers the execution layer to create calendar events. All external calls (Supabase, Google Calendar) are backend-only.

---

## AI Agent System

| Agent | Role |
|-------|------|
| **Supervisor Agent** | Orchestrates the crew, synthesizes sub-agent outputs into a full-day plan, and computes a confidence score. Decides whether to auto-execute (create calendar events) or request human confirmation. |
| **Schedule Agent** | Identifies academic priorities and task ordering from profile, events, and memory. |
| **Logistics Agent** | Suggests commute routes and timing based on commute mode and schedule. |
| **Preference Agent** | Recommends meals and dietary choices from the user's diet and preferences. |
| **Execution Agent** | Runs after supervisor approval: fetches the user's Google token, converts the plan to calendar events, and inserts them via the Google Calendar API. Logs executions in Supabase. |

The supervisor evaluates sub-agent outputs and calculates a **confidence score** before any calendar actions. Only when confidence meets the configured threshold (e.g. 0.7) does the execution agent create events; otherwise the UI can show a manual confirmation path.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18, Vite, Material-UI, Framer Motion, Supabase JS client |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **AI Infrastructure** | CrewAI, LiteLLM, OpenRouter (GPT-4o-mini, Claude 3 Haiku, Llama 3.1 8B) |
| **Database & Auth** | Supabase (PostgreSQL, Auth), Google OAuth 2.0 |
| **External APIs** | Google Calendar API (event creation) |

---

## Project Structure

```
morning-planner-agentic-ai/
├── backend/
│   ├── agents/
│   │   ├── supervisor.py        # Orchestration and confidence gate
│   │   ├── crewai_agents.py     # Schedule, Logistics, Preference, Supervisor agents
│   │   ├── execution.py        # Post-plan execution logic
│   │   └── tool_execution/      # LangChain tools (e.g. calendar)
│   ├── memory/
│   │   └── simple_memory.py    # Supabase memory read/write
│   ├── main.py                 # FastAPI app and routes
│   ├── db.py                   # Supabase client
│   ├── llm_factory.py          # LiteLLM/OpenRouter config
│   ├── google_calendar_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── LoginScreen.jsx
│   │   └── supabaseClient.js
│   ├── public/
│   ├── package.json
│   └── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## How It Works

1. **User login** — User signs in with Google via Supabase Auth. Session is established; backend can identify the user by `user_id`.
2. **Profile stored** — User submits profile (diet, wake time, commute mode, focus goal) and optional events/memory. Data is stored in Supabase.
3. **Agents analyze** — On "Generate Plan", the backend loads profile, events, and memory, builds a context, and runs the CrewAI crew (Schedule, Logistics, Preference, then Supervisor for the full-day plan).
4. **Supervisor builds plan** — Supervisor produces a structured daily plan and a confidence score.
5. **Confidence check** — If score ≥ threshold, the execution agent runs; otherwise the system can flag for manual review.
6. **Calendar events created** — Execution agent fetches the user's Google Calendar token from Supabase, maps the plan to events with start/end times, and creates them via the Google Calendar API. Results are logged in Supabase.

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/create-user` | Create or update user profile. |
| `GET` | `/get-profile?user_id=` | Fetch profile (including `calendar_connected` flag). |
| `GET` | `/morning-plan?user_id=` | Run the full pipeline: agents + supervisor + optional calendar execution. Returns plan and execution summary. |
| `GET` | `/plans?user_id=` | List recent generated plans. |
| `POST` | `/add-memory` | Store a personal memory entry. |
| `POST` | `/api/store-google-token` | Store the user's Google Calendar OAuth token. |
| `POST` | `/api/execute-calendar-plan` | Manually trigger calendar event creation from a plan payload. |
| `POST` | `/upsert-auth-user` | Sync Supabase Auth user (e.g. after Google login). |

Interactive API docs: `http://localhost:8000/docs`.

---

## Setup Instructions

**Prerequisites:** Git, Node.js 18+, Python 3.10+, and accounts for Supabase, OpenRouter, and Google Cloud (for Calendar API and OAuth).

**1. Clone the repository**

```bash
git clone https://github.com/Rithik-Sharon-A/morning-planner-agentic-ai.git
cd morning-planner-agentic-ai
```

**2. Backend**

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env: OPENROUTER_API_KEY, SUPABASE_*, GOOGLE_CLIENT_*, etc.

python main.py
```

Backend: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

**3. Frontend**

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL, VITE_GOOGLE_CLIENT_ID

npm run dev
```

Frontend: `http://localhost:5173`

**4. Environment variables**

- **Backend (`.env`):** `OPENROUTER_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `CONFIDENCE_THRESHOLD`, `*_MODEL` (per-agent), `CORS_ORIGINS`.
- **Frontend (`.env`):** `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`.

Use `backend/.env.example` and `frontend/.env.example` as templates. Never commit real keys.

---

## Deployment

**Backend (e.g. Railway, Render, Fly.io):** Set all backend env vars in the platform dashboard. Build from repo; install with `pip install -r requirements.txt`. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Ensure the production frontend origin is in `CORS_ORIGINS`.

**Frontend (e.g. Vercel, Netlify):** Build command `npm run build`, output directory `dist`. Set `VITE_API_URL` to the deployed backend URL and configure `VITE_SUPABASE_*` and `VITE_GOOGLE_CLIENT_ID`. Add the production frontend URL to Google OAuth authorized origins and Supabase redirect URLs.

---

## License

MIT License. See [LICENSE](LICENSE) in the repository.

---

## Author

**Rithik Sharon A**  
([Vibecoderithik](https://github.com/Rithik-Sharon-A))

Independently designed and developed as an agentic AI system demonstrating multi-agent orchestration, automated planning, and real-world API integrations (Supabase, Google Calendar).
