import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from llm_factory import make_llm

load_dotenv()

# Model names from env (OpenRouter only)
SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL", "openai/gpt-4-turbo")
PREFERENCE_MODEL = os.getenv("PREFERENCE_MODEL", "meta-llama/llama-3.1-8b-instruct")
LOGISTICS_MODEL  = os.getenv("LOGISTICS_MODEL", "openai/gpt-4o-mini")
SCHEDULE_MODEL   = os.getenv("SCHEDULE_MODEL", "anthropic/claude-3.5-sonnet")

# Shared agents — created once, used by run_crew
supervisor_agent = Agent(
    role="Supervisor Agent",
    goal="Synthesise sub-agent outputs into a coherent morning plan.",
    backstory="Senior coordinator who combines schedule, logistics, and preference insights.",
    llm=make_llm(SUPERVISOR_MODEL),
    verbose=False,
    allow_delegation=False,
)

preference_agent = Agent(
    role="Preference Agent",
    goal="Recommend a meal based on the student's dietary preferences.",
    backstory="Nutritionist specialising in student dietary habits.",
    llm=make_llm(PREFERENCE_MODEL),
    verbose=False,
    allow_delegation=False,
)

logistics_agent = Agent(
    role="Logistics Agent",
    goal="Plan the best commute route for the student today.",
    backstory="Expert in urban logistics and student commute planning.",
    llm=make_llm(LOGISTICS_MODEL),
    verbose=False,
    allow_delegation=False,
)

schedule_agent = Agent(
    role="Schedule Agent",
    goal="Identify today's academic priorities based on student context.",
    backstory="Expert academic scheduler for university students.",
    llm=make_llm(SCHEDULE_MODEL),
    verbose=False,
    allow_delegation=False,
)

print("[OK] CrewAI agents initialized via OpenRouter")


def run_crew(context: str) -> dict:
    """Run the crew using the shared agents. All LLMs via OpenRouter."""
    schedule_task = Task(
        description=(
            f"Student context: {context}\n"
            "Generate today's academic priorities in 1–2 sentences."
        ),
        expected_output="1-2 sentence academic priority statement.",
        agent=schedule_agent,
    )

    logistics_task = Task(
        description=(
            f"Student context: {context}\n"
            "Suggest a commute route in 1–2 sentences."
        ),
        expected_output="1-2 sentence commute route recommendation.",
        agent=logistics_agent,
    )

    preference_task = Task(
        description=(
            f"Student context: {context}\n"
            "Suggest a meal based on the student's diet in 1–2 sentences."
        ),
        expected_output="1-2 sentence meal recommendation.",
        agent=preference_agent,
    )

    reasoning_task = Task(
        description=(
            "Given the schedule, logistics, and preference agent outputs, "
            "write a 2–3 sentence explanation of the final morning plan."
        ),
        expected_output="2-3 sentence supervisor reasoning.",
        agent=supervisor_agent,
        context=[schedule_task, logistics_task, preference_task],
    )

    crew = Crew(
        agents=[schedule_agent, logistics_agent, preference_agent, supervisor_agent],
        tasks=[schedule_task, logistics_task, preference_task, reasoning_task],
        verbose=False,
    )

    result = crew.kickoff()

    schedule_out   = str(schedule_task.output.raw   if schedule_task.output   else "")
    logistics_out  = str(logistics_task.output.raw  if logistics_task.output  else "")
    preference_out = str(preference_task.output.raw if preference_task.output else "")
    reasoning      = str(reasoning_task.output.raw  if reasoning_task.output  else str(result))

    return {
        "schedule_out":   schedule_out,
        "logistics_out":  logistics_out,
        "preference_out": preference_out,
        "reasoning":      reasoning,
    }
