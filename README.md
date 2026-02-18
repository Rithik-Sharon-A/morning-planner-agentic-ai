# Morning Planner - Agentic AI Student Life Planner

A production-grade autonomous multi-agent system that helps students optimize their morning routines through AI-powered decision-making with persistent memory storage.

## Overview

Morning Planner is an intelligent system that coordinates multiple specialized AI agents to generate personalized morning plans for students. The system analyzes user preferences, daily schedules, and logistics to provide actionable recommendations for meals, commute routes, and task prioritization.

## Key Features

### Multi-Agent Architecture
- **Supervisor Agent**: Orchestrates all sub-agents and synthesizes final decisions
- **Schedule Agent**: Analyzes academic calendar and determines task priorities
- **Logistics Agent**: Plans optimal commute routes and meal recommendations
- **Preference Agent**: Applies dietary restrictions and lifestyle preferences

### AI Integration
- **OpenRouter Support**: Unified API access to multiple LLM providers
- **Model Flexibility**: Switch between GPT-4, Claude, Llama without code changes
- **Real-time Generation**: All agent outputs generated dynamically via LLM calls
- **No Hardcoded Responses**: Pure AI-driven decision making

### Persistent Memory
- **User Profiles**: Store dietary preferences, commute mode, wake time, and focus goals
- **Daily Events**: Track academic schedules, assignments, and deadlines
- **Plan History**: Maintain record of all generated plans with timestamps
- **Context-Aware**: Agents use stored data to personalize recommendations

### Autonomous Decision Making
- **Confidence Scoring**: System calculates confidence level for each decision
- **Human-in-the-Loop**: Requests human confirmation when confidence falls below threshold
- **Transparent Reasoning**: Provides natural language explanations for all decisions
- **Agent Logs**: Detailed reasoning from each specialized agent

## System Architecture

### Data Flow

```
User Input (React Frontend)
    |
    v
FastAPI REST API
    |
    v
Supervisor Agent (Coordinator)
    |
    +-- Schedule Agent  --> OpenRouter API --> LLM Response
    +-- Logistics Agent --> OpenRouter API --> LLM Response
    +-- Preference Agent --> OpenRouter API --> LLM Response
    |
    v
Supervisor Synthesis --> OpenRouter API --> Final Reasoning
    |
    v
Supabase Database (Persistent Storage)
    |
    v
Structured JSON Response
    |
    v
React UI (Visualization)
```

### Component Interaction

1. **User submits profile** via React form
2. **Backend creates user record** in Supabase
3. **Daily events stored** linked to user ID
4. **Supervisor fetches context** from database
5. **Three agents execute in parallel** via OpenRouter
6. **Supervisor aggregates outputs** and generates reasoning
7. **Plan stored in database** with timestamp
8. **Response returned** to frontend with all agent logs

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework with automatic API documentation
- **OpenAI SDK**: Client library for OpenRouter API integration
- **Supabase Python Client**: PostgreSQL database with real-time capabilities
- **Python-dotenv**: Environment variable management
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Component-based UI library
- **Vite**: Next-generation frontend build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Native Fetch API**: HTTP client for API communication

### Infrastructure
- **OpenRouter**: Unified gateway to multiple LLM providers
- **Supabase**: Backend-as-a-Service with PostgreSQL
- **Uvicorn**: ASGI server for FastAPI applications

## Installation and Setup

### Backend Installation

#### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenRouter Configuration (Required)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Supabase Configuration (Required)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Application Configuration
CONFIDENCE_THRESHOLD=0.7
API_HOST=0.0.0.0
API_PORT=8000
```

#### Step 5: Run Backend Server

```bash
python main.py
```

Server will start on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

### Frontend Installation

#### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

#### Step 2: Run Development Server

```bash
npm run dev
```

Frontend will start on `http://localhost:5173`

### Database Setup

#### Create Supabase Tables

Execute the following SQL in your Supabase SQL Editor:

```sql
-- User profiles table
CREATE TABLE user_profile (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  diet TEXT NOT NULL,
  commute_mode TEXT NOT NULL,
  wake_time TEXT NOT NULL,
  focus_goal TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily events table
CREATE TABLE daily_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  event_text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated plans table
CREATE TABLE generated_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES user_profile(id) ON DELETE CASCADE,
  plan JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_daily_events_user_id ON daily_events(user_id);
CREATE INDEX idx_generated_plans_user_id ON generated_plans(user_id);
CREATE INDEX idx_generated_plans_created_at ON generated_plans(created_at DESC);
```

#### Disable Row-Level Security (MVP Only)

For rapid development, disable RLS on all tables:

1. Navigate to Table Editor in Supabase Dashboard
2. Select each table (user_profile, daily_events, generated_plans)
3. Click the shield icon
4. Toggle "Enable RLS" to OFF

**Note:** For production deployment, implement proper RLS policies instead.

## API Reference

### POST /create-user

Create a new user profile.

**Request Body:**
```json
{
  "diet": "Vegan",
  "commute_mode": "Bus",
  "wake_time": "7:00 AM",
  "focus_goal": "Study for exams"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### POST /add-event

Add a daily event for a user.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_text": "9 AM lecture, 12 PM assignment deadline"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### GET /get-profile

Retrieve user profile by ID.

**Query Parameters:**
- `user_id` (required): UUID of the user

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "diet": "Vegan",
  "commute_mode": "Bus",
  "wake_time": "7:00 AM",
  "focus_goal": "Study for exams",
  "created_at": "2026-02-18T10:00:00Z"
}
```

### GET /morning-plan

Generate a morning plan for a user.

**Query Parameters:**
- `user_id` (optional): UUID of the user

**Response:**
```json
{
  "meal": "Oatmeal with berries and almond milk",
  "route": "Take Bus 42 from Main St, arrive campus in 25 minutes",
  "priority": "Attend 9 AM lecture, complete assignment by noon",
  "confidence": 0.85,
  "reasoning": "Your morning schedule includes important academic tasks. Based on your vegan diet preference, I selected a nutritious plant-based breakfast. The bus route is optimal given current traffic conditions.",
  "agent_logs": {
    "schedule": "Detected lecture at 9 AM and assignment deadline at noon",
    "logistics": "Selected Bus 42 route with 25-minute travel time and vegan breakfast option",
    "preference": "Applied vegan dietary restrictions and morning focus preferences"
  },
  "needs_human": false
}
```

### GET /plans

Retrieve recent generated plans for a user.

**Query Parameters:**
- `user_id` (required): UUID of the user

**Response:**
```json
[
  {
    "id": "plan-uuid-1",
    "user_id": "user-uuid",
    "plan": { /* full plan object */ },
    "created_at": "2026-02-18T08:00:00Z"
  },
  {
    "id": "plan-uuid-2",
    "user_id": "user-uuid",
    "plan": { /* full plan object */ },
    "created_at": "2026-02-17T08:00:00Z"
  }
]
```

## Agent Implementation Details

### Supervisor Agent

**Responsibilities:**
- Initialize OpenRouter client
- Coordinate execution of all sub-agents
- Fetch user context from Supabase
- Inject context into agent prompts
- Synthesize final decision
- Generate natural language reasoning
- Calculate confidence scores

**Decision Logic:**
```python
1. Fetch user profile and events from Supabase
2. Build context string with user data
3. Call Schedule Agent with context
4. Call Logistics Agent with context
5. Call Preference Agent with context
6. Call Supervisor LLM to synthesize outputs
7. Return structured decision with reasoning
```

### Schedule Agent

**Purpose:** Analyze academic calendar and determine priorities

**Input:** User context (schedule, events, focus goals)

**Output:** 1-2 sentence priority statement

**Example:** "Attend 9 AM Data Structures lecture and complete Project 1 by noon deadline"

### Logistics Agent

**Purpose:** Plan commute routes and meal recommendations

**Input:** User context (commute mode, diet, wake time)

**Output:** 1-2 sentence logistics plan

**Example:** "Take Bus 42 from Main Street (25 min) and have oatmeal with berries for breakfast"

### Preference Agent

**Purpose:** Apply dietary restrictions and lifestyle preferences

**Input:** User context (diet, preferences, habits)

**Output:** 1-2 sentence preference analysis

**Example:** "Applied vegan dietary restrictions and selected high-protein breakfast options"

## OpenRouter Configuration

### Model Selection

The system uses OpenRouter to access multiple LLM providers through a single API.

**Recommended Models by Use Case:**

**Development (Fast & Low Cost):**
- `openai/gpt-4o-mini` - $0.15 per 1M tokens
- `anthropic/claude-3-haiku` - $0.25 per 1M tokens
- `meta-llama/llama-3.1-8b-instruct` - $0.20 per 1M tokens

**Production (Balanced Performance):**
- `openai/gpt-4-turbo` - $10 per 1M tokens
- `anthropic/claude-3.5-sonnet` - $3 per 1M tokens (excellent reasoning)
- `meta-llama/llama-3.1-70b-instruct` - $0.35 per 1M tokens

**Premium (Maximum Quality):**
- `openai/gpt-4` - $30 per 1M tokens
- `anthropic/claude-3-opus` - $15 per 1M tokens

### Switching Models

Change the model by updating `.env`:

```env
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

Restart the backend server. No code changes required.

## User Flow

### First-Time User

1. User opens application
2. Fills profile form with diet, commute mode, wake time, focus goal
3. Enters today's events in textarea
4. Clicks "Save Profile & Generate Plan"
5. Backend creates user profile in Supabase
6. Backend stores daily events
7. User ID saved to browser localStorage
8. Agents generate personalized morning plan
9. Plan displayed with confidence score and reasoning
10. Plan saved to database for history

### Returning User

1. User opens application
2. System detects stored user ID in localStorage
3. Profile automatically loaded and displayed in "Loaded From Memory" section
4. Previous plan automatically fetched
5. Recent plans (last 3) displayed in history section
6. User can regenerate new plan or approve existing plan

## UI Components

### Profile Form
- Diet preference input
- Commute mode selection
- Wake time specification
- Focus goal definition
- Today's events textarea
- Save and generate button

### Loaded From Memory Section
- Displays saved user profile
- Shows diet, commute mode, wake time, focus goal
- Only visible when profile exists
- Light bordered box with subtle background

### Morning Plan Display
- **Meal Card**: Breakfast recommendation
- **Route Card**: Commute instructions with time estimate
- **Priority Card**: Top academic tasks for the morning
- **Confidence Bar**: Visual progress bar showing AI confidence level
- **Supervisor Reasoning**: Natural language explanation of decisions
- **Agent Reasoning**: Expandable section with individual agent logs

### Recent Plans History
- Last 3 generated plans displayed
- Timestamp for each plan
- Summary preview (first 120 characters)
- Confidence score indicator
- Expandable cards showing full details
- Click to expand/collapse individual plans

### Status Indicators
- **Agents Active Badge**: Green pulsing indicator showing system status
- **Architecture Viewer**: Modal overlay showing system flow diagram
- **Loading States**: Clear feedback during API calls
- **Error Messages**: User-friendly error notifications

### Action Buttons
- **Approve Plan**: Confirms and executes the morning plan
- **Regenerate**: Fetches new plan using existing profile

## Configuration

### Environment Variables

#### Backend Configuration

Create `backend/.env`:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Supabase Database Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Application Settings
CONFIDENCE_THRESHOLD=0.7
API_HOST=0.0.0.0
API_PORT=8000
```

#### Frontend Configuration

The frontend automatically connects to `http://localhost:8000`. To change the backend URL, modify the `BASE` constant in `src/App.jsx`.

### Confidence Threshold

The `CONFIDENCE_THRESHOLD` determines when the system requests human input:

- **0.7 (default)**: Balanced - requests input for uncertain decisions
- **0.5**: Lenient - more autonomous, fewer human confirmations
- **0.9**: Strict - requests input for most decisions

## Database Schema

### user_profile

Stores user preferences and settings.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| diet | TEXT | Dietary preferences (e.g., "Vegan", "Vegetarian") |
| commute_mode | TEXT | Transportation method (e.g., "Bus", "Car") |
| wake_time | TEXT | Preferred wake time (e.g., "7:00 AM") |
| focus_goal | TEXT | Daily focus objective (e.g., "Study for exams") |
| created_at | TIMESTAMP | Record creation timestamp |

### daily_events

Stores user's daily schedule and events.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| user_id | UUID | Foreign key to user_profile |
| event_text | TEXT | Event description |
| created_at | TIMESTAMP | Record creation timestamp |

### generated_plans

Stores all generated morning plans.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| user_id | UUID | Foreign key to user_profile |
| plan | JSONB | Complete plan object with all fields |
| created_at | TIMESTAMP | Plan generation timestamp |

## API Endpoints

### Health Check

**GET /**

Returns system status.

**Response:**
```json
{
  "status": "Morning Agent Running"
}
```

### User Management

**POST /create-user**

Creates new user profile.

**Request:**
```json
{
  "diet": "Vegan",
  "commute_mode": "Bus",
  "wake_time": "7:00 AM",
  "focus_goal": "Study for exams"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**GET /get-profile**

Retrieves user profile.

**Query Parameters:**
- `user_id`: User UUID (required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "diet": "Vegan",
  "commute_mode": "Bus",
  "wake_time": "7:00 AM",
  "focus_goal": "Study for exams",
  "created_at": "2026-02-18T10:00:00Z"
}
```

### Event Management

**POST /add-event**

Adds daily event for user.

**Request:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_text": "9 AM lecture, 12 PM assignment deadline"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### Plan Generation

**GET /morning-plan**

Generates personalized morning plan.

**Query Parameters:**
- `user_id`: User UUID (optional)

**Response:**
```json
{
  "meal": "Oatmeal with berries and almond milk",
  "route": "Take Bus 42 from Main Street, arrive campus in 25 minutes",
  "priority": "Attend 9 AM Data Structures lecture, complete Project 1 by noon",
  "confidence": 0.85,
  "reasoning": "Your morning schedule includes critical academic commitments. Based on your vegan diet preference, I selected a nutritious plant-based breakfast. The bus route is optimal given current traffic conditions and your 7 AM wake time.",
  "agent_logs": {
    "schedule": "Detected lecture at 9 AM and assignment deadline at noon requiring immediate attention",
    "logistics": "Selected Bus 42 route with 25-minute travel time and recommended vegan breakfast options",
    "preference": "Applied vegan dietary restrictions and morning study focus preferences"
  },
  "needs_human": false
}
```

**GET /plans**

Retrieves recent generated plans.

**Query Parameters:**
- `user_id`: User UUID (required)

**Response:**
```json
[
  {
    "id": "plan-uuid-1",
    "user_id": "user-uuid",
    "plan": {
      "meal": "...",
      "route": "...",
      "priority": "...",
      "confidence": 0.85,
      "reasoning": "...",
      "agent_logs": { }
    },
    "created_at": "2026-02-18T08:00:00Z"
  }
]
```

## Agent Prompts

### Schedule Agent Prompt

```
You are a Schedule Agent. [User context: diet, commute, wake time, focus goal, events]
Generate today's academic priorities for this student in 1-2 sentences.
```

### Logistics Agent Prompt

```
You are a Logistics Agent. [User context: diet, commute, wake time, focus goal, events]
Suggest a healthy breakfast and a commute route for this student in 1-2 sentences.
```

### Preference Agent Prompt

```
You are a Preference Agent. [User context: diet, commute, wake time, focus goal, events]
Suggest food choices based on this student's healthy habits and diet in 1-2 sentences.
```

### Supervisor Synthesis Prompt

```
You are a Supervisor Agent. Given the following sub-agent outputs, write a 2-3 sentence 
natural language explanation of the final morning plan.

Schedule Agent: [output]
Logistics Agent: [output]
Preference Agent: [output]

Explanation:
```

## Development Workflow

### Making Changes

1. **Modify agent logic**: Edit files in `backend/agents/`
2. **Update API endpoints**: Modify `backend/main.py`
3. **Change UI components**: Edit `frontend/src/App.jsx`
4. **Adjust styling**: Update Tailwind classes in JSX

### Testing

**Test Backend:**
```bash
# Activate venv
cd backend
venv\Scripts\activate

# Run server
python main.py

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/morning-plan
```

**Test Frontend:**
```bash
cd frontend
npm run dev
# Open http://localhost:5173
```

### Building for Production

**Backend:**
```bash
# Use production ASGI server
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
npm run build
# Serve dist/ folder with nginx or similar
```

## Troubleshooting

### Backend Issues

**Error: ModuleNotFoundError: No module named 'supabase'**

Solution: Activate virtual environment before running
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Error: Row-level security policy violation**

Solution: Disable RLS on Supabase tables (see Database Setup section)

**Error: Invalid API key (OpenRouter)**

Solution: Verify `OPENROUTER_API_KEY` in `.env` is correct and starts with `sk-or-v1-`

**Error: 500 Internal Server Error on /create-user**

Solutions:
- Check Supabase URL and anon key are correct
- Verify tables exist in database
- Check server logs for detailed error message
- Ensure RLS is disabled on tables

### Frontend Issues

**Error: Failed to fetch morning plan**

Solutions:
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure `BASE` URL in App.jsx matches backend

**Blank screen or component not rendering**

Solutions:
- Check browser console for JavaScript errors
- Verify all dependencies installed: `npm install`
- Clear browser cache and reload

### Agent Issues

**Agents return "Agent unavailable"**

Solutions:
- Verify OpenRouter API key is valid
- Check OpenRouter service status: https://status.openrouter.ai
- Ensure sufficient API credits in OpenRouter account
- Test API key: `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer YOUR_KEY"`

**Confidence always 0.0**

This indicates agent execution failed. Check:
- OpenRouter API key validity
- Network connectivity
- Server logs for detailed error messages

## Performance Considerations

### API Call Optimization

The system makes 4 LLM calls per plan generation:
1. Schedule Agent call
2. Logistics Agent call
3. Preference Agent call
4. Supervisor synthesis call

**Estimated latency:** 3-5 seconds per plan generation

**Cost per plan:** ~$0.001 with gpt-4o-mini

### Caching Strategies

For production, consider:
- Cache user profiles in memory
- Implement Redis for session management
- Add response caching for repeated queries
- Use CDN for frontend assets

### Database Optimization

Indexes are created on:
- `daily_events.user_id`
- `generated_plans.user_id`
- `generated_plans.created_at`

For high traffic, consider:
- Connection pooling
- Read replicas
- Query optimization
- Archiving old plans

## Security Best Practices

### Development
- Never commit `.env` files to version control
- Use `.gitignore` to exclude sensitive files
- Rotate API keys regularly
- Use separate keys for dev/staging/prod

### Production
- Enable Supabase Row-Level Security with proper policies
- Implement user authentication (JWT, OAuth)
- Configure CORS for specific domains only
- Use HTTPS for all communications
- Set rate limiting on API endpoints
- Monitor API usage and costs
- Implement request validation and sanitization

### Recommended RLS Policies (Production)

```sql
-- User can only read their own profile
CREATE POLICY "Users can read own profile"
ON user_profile FOR SELECT
USING (auth.uid() = id);

-- User can only insert their own events
CREATE POLICY "Users can insert own events"
ON daily_events FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- User can only read their own plans
CREATE POLICY "Users can read own plans"
ON generated_plans FOR SELECT
USING (auth.uid() = user_id);
```

## Deployment

### Backend Deployment Options

**Option 1: Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Option 2: Render**
- Connect GitHub repository
- Set environment variables in dashboard
- Deploy with automatic HTTPS

**Option 3: AWS EC2**
- Launch Ubuntu instance
- Install Python and dependencies
- Use systemd for process management
- Configure nginx as reverse proxy

### Frontend Deployment Options

**Option 1: Vercel**
```bash
npm i -g vercel
vercel
```

**Option 2: Netlify**
```bash
npm run build
# Drag dist/ folder to Netlify dashboard
```

**Option 3: GitHub Pages**
```bash
npm run build
# Deploy dist/ folder to gh-pages branch
```

## Monitoring and Observability

### Recommended Metrics

- API response times
- Agent execution success rate
- Confidence score distribution
- User engagement (plans generated per user)
- Error rates by endpoint
- LLM API costs
- Database query performance

### Logging

Backend logs include:
- Agent execution traces
- LLM API call results
- Database operation status
- Error stack traces

Access logs via:
```bash
# View server logs
tail -f backend/logs/app.log

# Or run with verbose output
python main.py --log-level debug
```

## Testing

### Manual Testing

**Test user creation:**
```bash
curl -X POST http://localhost:8000/create-user \
  -H "Content-Type: application/json" \
  -d '{"diet":"Vegan","commute_mode":"Bus","wake_time":"7:00 AM","focus_goal":"Study"}'
```

**Test plan generation:**
```bash
curl "http://localhost:8000/morning-plan?user_id=YOUR_USER_ID"
```

### Automated Testing

For production, implement:
- Unit tests for agent functions
- Integration tests for API endpoints
- End-to-end tests for user flows
- Load testing for performance validation

## Project Structure

```
student-life-planner/
│
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── db.py                   # Supabase client initialization
│   ├── .env                    # Environment configuration (not in git)
│   ├── requirements.txt        # Python dependencies
│   ├── README.md              # Backend-specific documentation
│   │
│   └── agents/
│       ├── __init__.py        # Package initialization
│       ├── supervisor.py      # Supervisor agent (orchestrator)
│       ├── schedule.py        # Schedule analysis agent
│       ├── logistics.py       # Route and meal planning agent
│       └── preference.py      # Preference application agent
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Tailwind CSS imports
│   │
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── README.md              # Frontend-specific documentation
│
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## Dependencies

### Backend Dependencies

```
fastapi==0.129.0              # Web framework
uvicorn==0.41.0               # ASGI server
openai==1.83.0                # OpenRouter client
python-dotenv==1.1.1          # Environment variables
pydantic==2.11.10             # Data validation
supabase==2.28.0              # Database client
```

### Frontend Dependencies

```
react: ^18.3.1                # UI library
react-dom: ^18.3.1            # React DOM renderer
vite: ^7.3.1                  # Build tool
@tailwindcss/vite: latest     # Tailwind integration
```

## Contributing

This project is an MVP built for hackathon/educational purposes. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

### Phase 1 (Current - MVP)
- Basic multi-agent coordination
- OpenRouter integration
- Supabase persistence
- Simple React UI

### Phase 2 (Planned)
- User authentication and authorization
- Calendar integration (Google Calendar, Outlook)
- Real-time traffic data integration
- Weather-based recommendations
- Mobile responsive design improvements

### Phase 3 (Future)
- Mobile native apps (iOS/Android)
- Push notifications for plan updates
- Team/group planning features
- Advanced analytics dashboard
- A/B testing for different models
- Voice interface integration
- Slack/Discord bot integration

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments

- OpenRouter for unified LLM API access
- Supabase for backend infrastructure
- FastAPI for excellent Python web framework
- React and Vite for modern frontend development
- Tailwind CSS for utility-first styling

## Support and Documentation

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Supabase Documentation**: https://supabase.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **React Documentation**: https://react.dev

## Version History

### v1.0.0 (Current)
- Initial MVP release
- Multi-agent coordination system
- OpenRouter integration
- Supabase persistence
- React dashboard UI
- Profile management
- Plan history
- Confidence scoring
- Human-in-the-loop decision making

---

**Built for autonomous student life planning with AI agents**
