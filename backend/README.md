# Student Life Planner - Backend

A FastAPI-based backend service that uses CrewAI agents to help students plan their academic life.

## Features

- **Multi-Agent System**: Coordinates multiple specialized agents:
  - **Supervisor Agent**: Orchestrates all agents and synthesizes final plan
  - **Schedule Agent**: Optimizes academic schedules and study time
  - **Logistics Agent**: Plans transportation, meals, and campus resources
  - **Preference Agent**: Analyzes learning styles and personal preferences

- **Tool Execution Agent**: LangChain-based execution layer; writes events to Google Calendar when Supervisor confidence ≥ threshold.

- **OpenRouter Integration**: Access multiple AI models through one API (LLMs via LiteLLM/OpenRouter).

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Required: OpenRouter (LLMs via LiteLLM)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Required: Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional: Model overrides (defaults shown)
SUPERVISOR_MODEL=openai/gpt-4-turbo
SCHEDULE_MODEL=anthropic/claude-3.5-sonnet
LOGISTICS_MODEL=openai/gpt-4o-mini
PREFERENCE_MODEL=meta-llama/llama-3.1-8b-instruct

# Optional: Confidence threshold for auto-execution (default 0.7)
CONFIDENCE_THRESHOLD=0.7

# Optional: API server
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Google Calendar (for Tool Execution Agent)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
```

See [docs/GOOGLE_OAUTH_SETUP.md](docs/GOOGLE_OAUTH_SETUP.md) for Google Calendar OAuth setup.

## Running the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health / status |
| GET | `/models` | Return configured model names (debug) |
| POST | `/create-user` | Create or update user profile |
| GET | `/get-profile` | Get profile by `user_id` query |
| POST | `/add-event` | Add daily event text for user |
| POST | `/add-memory` | Add personal memory for user |
| GET | `/plans` | Get recent generated plans for user |
| GET | `/morning-plan` | Generate morning plan (Supervisor + crew + optional calendar execution) |
| POST | `/execute-calendar-events` | Run Tool Execution Agent to write events to Google Calendar |

### GET `/morning-plan?user_id=...`

Returns a decision object with `meal`, `route`, `priority`, `confidence`, `reasoning`, `agent_logs`, `models`, `execution` (ride/meal/calendar when applicable), and `needs_human` when confidence &lt; threshold.

### POST `/execute-calendar-events`

**Request body:**
```json
{
  "user_id": "optional-uuid",
  "events": [
    {
      "title": "Study session",
      "start_time": "2025-03-03T14:00:00Z",
      "end_time": "2025-03-03T16:00:00Z",
      "description": "CS101 revision"
    }
  ]
}
```

Datetimes must be ISO 8601 (e.g. `2025-03-03T09:00:00Z`).

## Project Structure

```
backend/
├── main.py                 # FastAPI app and routes
├── db.py                   # Supabase client
├── llm_factory.py          # OpenRouter LLM for CrewAI
├── tools.py                # Plan tools (ride, meal)
├── requirements.txt
├── run.ps1
├── agents/
│   ├── __init__.py
│   ├── supervisor.py       # Supervisor agent
│   ├── crewai_agents.py    # Schedule, Logistics, Preference, Supervisor (CrewAI)
│   ├── execution.py        # Plan execution + calendar gate
│   └── tool_execution/     # LangChain Tool Execution Agent
│       ├── agent.py
│       └── tools/
│           └── google_calendar.py
├── memory/
│   └── simple_memory.py    # User memories (Supabase)
├── docs/
│   ├── ARCHITECTURE_TOOL_EXECUTION.md
│   ├── GOOGLE_OAUTH_SETUP.md
│   └── CLEANUP_AND_REFACTOR_REPORT.md
└── scripts/
    └── safe_remove_unused_agents.ps1
```

## Development

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Technologies Used

- **FastAPI** – API framework
- **CrewAI** – Multi-agent orchestration
- **LangChain** – Tool Execution Agent (calendar tool)
- **LiteLLM / OpenRouter** – LLM access
- **Supabase** – Profile, events, plans, memories
- **Uvicorn** – ASGI server
