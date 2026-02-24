# Morning Planner – Autonomous Multi-Agent Student Life Planner

An agentic AI system that coordinates specialized agents to generate personalized morning plans. This is not a chatbot—it is an autonomous decision pipeline with persistent memory and tool execution.

---

## Key Highlights

- **Multi-agent architecture** — Supervisor + Schedule + Logistics + Preference + Execution agents
- **Multi-model reasoning** via OpenRouter (per-agent model config)
- **Persistent memory** using Supabase (profiles, events, plan history)
- **Autonomous execution** — ride booking (Rapido) + meal scheduling (FoodService) via Execution Agent
- **Confidence scoring** with human-in-the-loop when below threshold
- **Zero hardcoded responses** — all outputs from LLM calls

---

## Architecture Overview

```
User → Agents → Supervisor → Execution → Supabase → UI
```

The user submits profile and events. Sub-agents (Schedule, Logistics, Preference) reason independently via OpenRouter. The Supervisor synthesizes their outputs and produces a plan. The Execution Agent runs tools (mock Rapido, meal scheduler). Results and plan are stored in Supabase and returned to the React UI.

---

## Agents

| Agent | Responsibility |
|-------|----------------|
| **Supervisor Agent** | Orchestrates sub-agents, aggregates outputs, produces final reasoning and confidence |
| **Schedule Agent** | Determines task priorities from context and events |
| **Logistics Agent** | Plans commute route (e.g. bike/Rapido) |
| **Preference Agent** | Recommends meal based on diet and preferences |
| **Execution Agent** | Runs tools: book Rapido (when route implies ride), schedule meal |

---

## Tech Stack

**Backend:** FastAPI, Python, OpenRouter, Supabase  

**Frontend:** React, Vite, Tailwind  

**Tools:** Mock Rapido, Mock Meal Scheduler (FoodService)

---

## Demo Flow

1. User enters profile (diet, commute, wake time, focus goal) and optional events.
2. Data is stored in Supabase.
3. Schedule, Logistics, and Preference agents reason independently via OpenRouter.
4. Supervisor synthesizes outputs and computes confidence.
5. Execution Agent performs actions (Rapido booking if route mentions bike/Rapido, meal scheduling).
6. Confidence is returned; plan is stored.
7. Plan (meal, route, priority, execution, reasoning) is displayed in the UI.

---

## Why This Is Agentic

- **Independent agents** — Schedule, Logistics, and Preference each call the LLM with their own role and context; no single monolithic prompt.
- **Supervisor coordination** — One agent consumes sub-agent outputs and produces a final explanation and confidence score.
- **Tool execution** — The Execution Agent invokes tools (Rapido, FoodService) based on the plan; the system acts, not only responds.
- **Memory** — User profile and events live in Supabase; agents reason over stored context.
- **Confidence gating** — When confidence is below threshold, the system flags "Needs Human" for review.

**This is not a chatbot. It is an autonomous decision pipeline.**

---

## Running Locally

**Backend**

```bash
cd backend
pip install -r requirements.txt
# Set .env: OPENROUTER_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY, etc.
python main.py
```

API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

**Database:** Create Supabase project and tables (`user_profile`, `daily_events`, `generated_plans`) per your Supabase dashboard. Use the schema that matches the backend (e.g. `user_profile`: diet, commute_mode, wake_time, focus_goal; `daily_events`: user_id, event_text; `generated_plans`: user_id, plan JSONB).

---

## Future Improvements

- Calendar integration for real schedule sync
- Real Rapido / meal APIs instead of mocks
- Mobile app (React Native or PWA)
