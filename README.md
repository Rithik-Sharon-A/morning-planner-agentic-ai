# 🤖 AI Student Life Planner

> **An intelligent multi-agent system that generates optimized daily schedules and automatically executes approved plans by creating events in Google Calendar.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.129.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF6B6B)](https://www.crewai.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20DB-3ECF8E?logo=supabase)](https://supabase.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🧠 **Multi-Agent AI Architecture**
- **Supervisor Agent**: Orchestrates sub-agents and makes execution decisions
- **Schedule Agent**: Identifies academic priorities and task management
- **Logistics Agent**: Plans optimal commute routes and timing
- **Preference Agent**: Recommends meals based on dietary preferences
- **Execution Agent**: Automatically creates Google Calendar events

### 📅 **Intelligent Daily Planning**
- Full-day schedule generation from wake-up to sleep
- Adapts to user profile, preferences, and daily events
- Considers wake time, commute mode, diet, and focus goals
- Chronological timeline with 12-hour AM/PM format

### 🔐 **Secure Authentication**
- Google OAuth 2.0 via Supabase Auth
- Persistent user sessions
- Secure token management

### 💾 **Persistent Memory**
- User profiles stored in Supabase
- Personal notes and preferences
- Historical plan tracking
- Context-aware planning based on past interactions

### 📆 **Google Calendar Integration**
- Automatic event creation for approved plans
- OAuth 2.0 calendar access
- Configurable confidence threshold for auto-execution
- Manual override for low-confidence plans

### 🎨 **Modern UI/UX**
- Responsive React interface
- Real-time plan generation
- Visual pipeline progress tracking
- Dark mode with neon accents

---

## 🏗️ Architecture

```
┌─────────────┐
│   React     │  User Interface
│  Frontend   │  (Vite + Material-UI)
└──────┬──────┘
       │
       ↓ HTTP/REST
┌──────────────────────────────────────┐
│         FastAPI Backend              │
│  ┌────────────────────────────────┐  │
│  │    Supervisor Agent            │  │
│  │  (Confidence-based Execution)  │  │
│  └────────┬───────────────────────┘  │
│           ↓                          │
│  ┌────────────────────────────────┐  │
│  │   CrewAI Multi-Agent System    │  │
│  │  ┌──────────┐  ┌──────────┐   │  │
│  │  │Schedule  │  │Logistics │   │  │
│  │  │  Agent   │  │  Agent   │   │  │
│  │  └──────────┘  └──────────┘   │  │
│  │  ┌──────────┐  ┌──────────┐   │  │
│  │  │Preference│  │Execution │   │  │
│  │  │  Agent   │  │  Agent   │   │  │
│  │  └──────────┘  └──────────┘   │  │
│  └────────┬───────────────────────┘  │
│           ↓                          │
│  ┌────────────────────────────────┐  │
│  │   LiteLLM + OpenRouter         │  │
│  │  (GPT-4, Claude, Llama)        │  │
│  └────────────────────────────────┘  │
└──────────┬───────────────────────────┘
           │
           ↓
┌──────────────────────────────────────┐
│         External Services            │
│  ┌────────────┐  ┌────────────────┐  │
│  │  Supabase  │  │ Google Calendar│  │
│  │  (Auth+DB) │  │      API       │  │
│  └────────────┘  └────────────────┘  │
└──────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### **Frontend**
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **Framer Motion** - Animations
- **Supabase JS Client** - Authentication and database

### **Backend**
- **FastAPI** - Modern Python web framework
- **CrewAI** - Multi-agent orchestration
- **LiteLLM** - Unified LLM interface
- **OpenRouter** - LLM API gateway
- **Supabase Python Client** - Database operations
- **Google Calendar API** - Calendar integration

### **AI Models** (via OpenRouter)
- **GPT-4o-mini** - Supervisor and Logistics
- **Claude 3 Haiku** - Schedule planning
- **Llama 3.1 8B** - Preference recommendations

### **Database & Auth**
- **Supabase** - PostgreSQL database + Auth
- **Google OAuth 2.0** - User authentication

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Git** - [Download](https://git-scm.com/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.10+** - [Download](https://python.org/)
- **pip** - Python package manager (included with Python)

You'll also need accounts for:
- **Supabase** - [Sign up](https://supabase.com/)
- **OpenRouter** - [Sign up](https://openrouter.ai/)
- **Google Cloud Console** - [Console](https://console.cloud.google.com/)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-student-life-planner.git
cd ai-student-life-planner
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Start backend server
python main.py
```

Backend will run at: `http://localhost:8000`  
API docs available at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

### 4. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com/)
2. Run the SQL scripts in `backend/` to create tables:
   - `supabase_add_access_token.sql`
   - `supabase_execution_logs.sql`
3. Enable Google OAuth in Supabase Auth settings

---

## ⚙️ Configuration

### Backend Configuration (`backend/.env`)

```env
# OpenRouter Configuration
USE_OPENROUTER=true
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini

# Agent Models
SUPERVISOR_MODEL=openai/gpt-4o-mini
LOGISTICS_MODEL=openai/gpt-4o-mini
PREFERENCE_MODEL=meta-llama/llama-3.1-8b-instruct
SCHEDULE_MODEL=anthropic/claude-3-haiku

# Execution Settings
CONFIDENCE_THRESHOLD=0.7
API_HOST=0.0.0.0
API_PORT=8000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration (`frontend/.env`)

```env
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key

# Backend API
VITE_API_URL=http://localhost:8000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
```

### Getting API Keys

#### OpenRouter API Key
1. Sign up at [openrouter.ai](https://openrouter.ai/)
2. Navigate to API Keys
3. Create a new key
4. Add credits to your account

#### Supabase Credentials
1. Create project at [supabase.com](https://supabase.com/)
2. Go to Settings → API
3. Copy `Project URL` and `anon public` key
4. Copy `service_role` key (keep secret!)

#### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:5173`
   - Your production URL
6. Add authorized JavaScript origins:
   - `http://localhost:5173`
   - Your production URL
7. Copy Client ID and Client Secret

---

## 📁 Project Structure

```
ai-student-life-planner/
├── backend/
│   ├── agents/
│   │   ├── supervisor.py           # Supervisor orchestration
│   │   ├── crewai_agents.py        # Agent definitions
│   │   ├── execution.py            # Execution logic
│   │   └── tool_execution/         # LangChain tools
│   ├── memory/
│   │   └── simple_memory.py        # Memory management
│   ├── main.py                     # FastAPI application
│   ├── db.py                       # Supabase client
│   ├── llm_factory.py              # LLM initialization
│   ├── google_calendar_service.py  # Calendar integration
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment template
│   └── *.sql                       # Database schemas
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main application
│   │   ├── LoginScreen.jsx         # Authentication
│   │   └── supabaseClient.js       # Supabase config
│   ├── public/
│   │   └── favicon.svg             # App icon
│   ├── package.json                # Node dependencies
│   └── .env.example                # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── SUPABASE_AUTH_FIXES.md          # Auth troubleshooting
└── INFINITE_LOOP_FIXES.md          # Performance fixes
```

---

## 🔄 How It Works

### 1. **User Authentication**
- User clicks "Continue with Google"
- Supabase handles OAuth flow
- User profile created/updated in database

### 2. **Profile & Memory**
- User fills profile (diet, wake time, commute mode, focus goal)
- Optional: Add personal memory notes
- Data stored in Supabase for context

### 3. **Plan Generation**
- User clicks "Save Profile & Generate Plan"
- Backend fetches profile, events, and memories
- Supervisor coordinates 4 specialized agents:
  - **Schedule Agent**: Analyzes academic priorities
  - **Logistics Agent**: Plans commute and routes
  - **Preference Agent**: Suggests meals
  - **Supervisor Agent**: Synthesizes full-day timeline
- Agents use different LLMs for specialized reasoning

### 4. **Confidence-Based Execution**
- Supervisor calculates confidence score (0-1)
- If `confidence >= threshold` (default 0.7):
  - ✅ Auto-execute: Create Google Calendar events
  - ✅ Log execution to database
- If `confidence < threshold`:
  - ⚠️ Request human confirmation
  - 🔍 Show reasoning for review

### 5. **Calendar Integration**
- Fetch user's Google OAuth token from database
- Convert timeline to calendar events
- Create events in user's primary calendar
- Log each created event

---

## 📚 API Documentation

### Key Endpoints

#### `POST /create-user`
Create or update user profile
```json
{
  "user_id": "uuid",
  "diet": "Vegetarian",
  "commute_mode": "Bus",
  "wake_time": "7:00 AM",
  "focus_goal": "Study for exams"
}
```

#### `GET /morning-plan?user_id={uuid}`
Generate daily plan
```json
{
  "meal": "Oatmeal with fruits",
  "route": "Take bus #42 at 8:15 AM",
  "priority": "Focus on Math assignment",
  "confidence": 0.85,
  "daily_plan": [
    {"time": "7:00 AM", "activity": "Wake up"},
    {"time": "7:30 AM", "activity": "Breakfast"}
  ],
  "execution": {
    "calendar": {
      "status": "success",
      "events_created": 10
    }
  }
}
```

#### `POST /api/store-google-token`
Store Google Calendar OAuth token
```json
{
  "user_id": "uuid",
  "access_token": "ya29.a0..."
}
```

#### `POST /api/execute-calendar-plan`
Manually trigger calendar event creation
```json
{
  "user_id": "uuid",
  "events": [
    {"title": "Wake up", "time": "7:00 AM"}
  ]
}
```

Full API documentation: `http://localhost:8000/docs`

---

## 🚢 Deployment

### Backend Deployment (Railway/Render/Fly.io)

1. Set environment variables in platform dashboard
2. Deploy from GitHub repository
3. Ensure `requirements.txt` is present
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel/Netlify)

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables from `.env.example`
5. Update `VITE_API_URL` to production backend URL

### Environment Variables Checklist

**Backend:**
- ✅ `OPENROUTER_API_KEY`
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_ANON_KEY`
- ✅ `SUPABASE_SERVICE_ROLE_KEY`
- ✅ `GOOGLE_CLIENT_ID`
- ✅ `GOOGLE_CLIENT_SECRET`
- ✅ `CORS_ORIGINS` (add production frontend URL)

**Frontend:**
- ✅ `VITE_SUPABASE_URL`
- ✅ `VITE_SUPABASE_ANON_KEY`
- ✅ `VITE_API_URL` (production backend URL)
- ✅ `VITE_GOOGLE_CLIENT_ID`

---

## 🐛 Troubleshooting

### Common Issues

#### "Lock not released" errors
- **Cause**: Multiple `getUser()` calls
- **Fix**: See `SUPABASE_AUTH_FIXES.md`

#### Plans taking > 5 minutes
- **Cause**: Infinite loops or slow LLM responses
- **Fix**: See `INFINITE_LOOP_FIXES.md`

#### Google Calendar not connecting
- **Cause**: Missing OAuth scope or token
- **Fix**: 
  1. Ensure `VITE_GOOGLE_CLIENT_ID` is set
  2. Click "Connect Google Calendar" in UI
  3. Grant calendar permissions
  4. Check `user_profile.access_token` in database

#### Agents not using profile data
- **Cause**: Memory not being passed to agents
- **Fix**: Check `_build_memory_context` in `supervisor.py`

### Debug Mode

Enable verbose logging:
```python
# backend/agents/crewai_agents.py
crew = Crew(
    agents=[...],
    tasks=[...],
    verbose=True  # Enable detailed logs
)
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration framework
- **OpenRouter** - Unified LLM API
- **Supabase** - Backend-as-a-Service
- **FastAPI** - Modern Python web framework
- **React** - UI library

---

## 📞 Support

For issues, questions, or suggestions:
- 🐛 [Open an issue](https://github.com/yourusername/ai-student-life-planner/issues)
- 💬 [Discussions](https://github.com/yourusername/ai-student-life-planner/discussions)
- 📧 Email: your.email@example.com

---

**Built with ❤️ for students by students**
