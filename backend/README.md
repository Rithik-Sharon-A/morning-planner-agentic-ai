# Student Life Planner - Backend

A FastAPI-based backend service that uses CrewAI agents to help students plan their academic life.

## Features

- **Multi-Agent System**: Coordinates multiple specialized agents:
  - **Supervisor Agent**: Orchestrates all agents and synthesizes final plan
  - **Schedule Agent**: Optimizes academic schedules and study time
  - **Logistics Agent**: Plans transportation, meals, and campus resources
  - **Preference Agent**: Analyzes learning styles and personal preferences

- **OpenRouter Integration**: Access multiple AI models through one API:
  - Switch between GPT-4, Claude, Llama, and more
  - Automatic fallback to OpenAI if OpenRouter fails
  - Cost optimization by choosing appropriate models
  - See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for details

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

**Option A: Use OpenRouter (Recommended)**
```env
# OpenRouter Configuration
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Fallback to OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

**Option B: Use Direct OpenAI**
```env
# OpenAI Configuration
USE_OPENROUTER=false
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

📖 **See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for detailed OpenRouter configuration**

## Running the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### GET `/`
Health check endpoint

### POST `/generate-plan`
Generate a comprehensive student life plan

**Request Body:**
```json
{
  "classes": [
    {
      "name": "Data Structures",
      "time": "9:00 AM",
      "days": ["Monday", "Wednesday", "Friday"],
      "location": "Room 101"
    }
  ],
  "assignments": [
    {
      "name": "Project 1",
      "due_date": "2026-03-01",
      "priority": "high"
    }
  ],
  "exams": [
    {
      "name": "Midterm Exam",
      "date": "2026-03-15",
      "prep_time": "2 weeks"
    }
  ],
  "preferences": {
    "learning_style": "visual",
    "peak_hours": ["morning"],
    "study_duration": 50,
    "break_duration": 10,
    "social_study": false
  },
  "logistics": {
    "location": "Off-campus",
    "commute_time": "30 minutes"
  }
}
```

**Response:**
```json
{
  "schedule": {
    "weekly_plan": "...",
    "study_blocks": [],
    "class_times": [],
    "assignment_deadlines": []
  },
  "recommendations": [
    "Personalized study tips..."
  ],
  "logistics_plan": {
    "transportation": "...",
    "meals": "...",
    "resources": "..."
  },
  "study_tips": [
    "Follow the personalized schedule",
    "Take regular breaks"
  ]
}
```

### GET `/health`
Check API health status

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── agents/
    ├── __init__.py        # Package initialization
    ├── supervisor.py      # Supervisor agent
    ├── schedule.py        # Schedule optimization agent
    ├── logistics.py       # Logistics planning agent
    └── preference.py      # Preference analysis agent
```

## Development

### Testing the API

You can test the API using:

1. **Swagger UI**: Navigate to `http://localhost:8000/docs`
2. **ReDoc**: Navigate to `http://localhost:8000/redoc`
3. **cURL**:
```bash
curl -X POST "http://localhost:8000/generate-plan" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **CrewAI**: Multi-agent orchestration framework
- **LangChain**: LLM application framework
- **OpenAI**: GPT models for intelligent agents
- **Uvicorn**: ASGI server for FastAPI
