# Agentic Student Life Planner

A multi-agent AI planner that generates personalized morning routines using CrewAI. Each agent specializes in a distinct task (meal, logistics, schedule). Different LLMs are assigned per agent via OpenRouter. User memories are stored in Supabase and injected into planning.

**Highlights:** role-based agents, multi-model orchestration, persistent memory, clear frontend/backend separation. This is an autonomous decision pipeline, not a chatbot.

---

## 1. Overview

This system coordinates specialized CrewAI agents to produce morning plans from user profile and events. The Supervisor aggregates outputs from Schedule, Logistics, and Preference agents. Each agent uses a configurable model via OpenRouter (e.g. GPT-4 Turbo for the Supervisor, Claude for Schedule, Llama for Preference). User profile, events, and free-form memories are stored in Supabase and passed into the planning context. The frontend (React) talks only to the FastAPI backend; all LLM routing is OpenRouter-only with no native Anthropic, Gemini, or Llama SDKs.

---

## 2. Architecture

```
        React
          ↓
       FastAPI
          ↓
   CrewAI Supervisor
          ↓
     Sub Agents
  (Schedule / Logistics / Preference)
          ↓
       LiteLLM
          ↓
      OpenRouter
          ↓
  GPT / Claude / Llama

Supabase: user profile, events, plain-text memory, generated plans.
```

---

## 3. Tech Stack

| Layer    | Technologies |
|----------|--------------|
| **Frontend** | React, Vite, Tailwind |
| **Backend**  | FastAPI, CrewAI, LiteLLM (internal), OpenRouter, Supabase |
| **LLMs (examples)** | GPT-4 Turbo (Supervisor), Claude 3.5 Sonnet (Schedule), Llama 3.1 (Preference), GPT-4o-mini (Logistics) |

Models are configured per agent in `.env` and can be changed without code edits.

---

## 4. Agent Roles

| Agent | Role |
|-------|------|
| **Supervisor Agent** | Aggregates sub-agent outputs, computes confidence, requests human confirmation when below threshold. |
| **Preference Agent** | Meal suggestions based on diet and preferences. |
| **Logistics Agent** | Commute and route planning. |
| **Schedule Agent** | Task prioritization from context and events. |

Execution (e.g. mock ride/meal tools) runs after the crew returns the plan.

---

## 5. Environment Variables

Create a `.env` in `backend/` with at least:

```env
OPENROUTER_API_KEY=your_key_here
SUPERVISOR_MODEL=openai/gpt-4-turbo
PREFERENCE_MODEL=meta-llama/llama-3.1-8b-instruct
LOGISTICS_MODEL=openai/gpt-4o-mini
SCHEDULE_MODEL=anthropic/claude-3.5-sonnet

SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

Model IDs are OpenRouter model names; you can switch providers (e.g. different Claude or GPT variants) by changing these variables.

---

## 6. How to Run

**Backend**

```bash
cd backend
pip install -r requirements.txt
# Configure .env (see above)
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

**Database:** Create a Supabase project and tables: `user_profile` (diet, commute_mode, wake_time, focus_goal), `daily_events` (user_id, event_text), `generated_plans` (user_id, plan JSONB), `user_memories` (user_id, content, created_at) for plain-text memory.

---

## 7. Key Features

- **Multi-agent reasoning** — Schedule, Logistics, and Preference agents reason independently; Supervisor synthesizes.
- **Multi-model routing** — One OpenRouter API key; per-agent models via `.env`.
- **Persistent user memory** — Supabase stores profile, events, and free-text memories used in planning.
- **Human-in-the-loop** — Confidence score and “Needs Human” when below threshold.
- **Modular agent design** — All agents defined in `backend/agents/crewai_agents.py` using a shared LLM factory.

---

## 8. What Was Intentionally Removed

To keep the system stable and simple:

- **LangChain** — Removed; orchestration is CrewAI-only.
- **Vector databases** — Removed; no embeddings or vector storage.
- **RAG** — Removed; no retrieval-augmented generation.

Memory is plain-text in Supabase; no embedding or vector dependencies.

---

## 9. Resume / Hackathon Description

*Built a multi-agent AI planner using CrewAI with role-based model specialization via OpenRouter and persistent Supabase-backed memory.*

---

## License

See repository for license information.
