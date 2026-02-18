from openai import OpenAI
import os
from dotenv import load_dotenv
from . import schedule, logistics, preference

load_dotenv()


class SupervisorAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    def get_decision(self, profile: dict = None, events: list = None):
        try:
            # Build context string injected into every sub-agent prompt
            context = self._build_context(profile, events)

            schedule_out   = schedule.get_output(self.client, self.model, context)
            logistics_out  = logistics.get_output(self.client, self.model, context)
            preference_out = preference.get_output(self.client, self.model, context)

            # Supervisor summary
            summary = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": (
                        "You are a Supervisor Agent. Given these sub-agent outputs, "
                        "write a 2–3 sentence natural language explanation of the final morning plan.\n\n"
                        f"Context: {context}\n"
                        f"Schedule Agent: {schedule_out}\n"
                        f"Logistics Agent: {logistics_out}\n"
                        f"Preference Agent: {preference_out}\n\n"
                        "Explanation:"
                    )
                }]
            )
            reasoning = summary.choices[0].message.content.strip()

            return {
                "meal":       logistics_out,
                "route":      logistics_out,
                "priority":   schedule_out,
                "confidence": 0.75,
                "reasoning":  reasoning,
                "agent_logs": {
                    "schedule":   schedule_out,
                    "logistics":  logistics_out,
                    "preference": preference_out,
                },
            }

        except Exception as e:
            return self._fallback(str(e))

    def _build_context(self, profile: dict, events: list) -> str:
        parts = []
        if profile:
            parts.append(
                f"User profile — diet: {profile.get('diet')}, "
                f"commute: {profile.get('commute_mode')}, "
                f"wake time: {profile.get('wake_time')}, "
                f"focus goal: {profile.get('focus_goal')}."
            )
        if events:
            parts.append(f"Today's events: {', '.join(events)}.")
        return " ".join(parts) if parts else "No user context provided."

    def _fallback(self, error=""):
        return {
            "meal":       "Unable to fetch meal recommendation",
            "route":      "Unable to fetch route",
            "priority":   "Unable to fetch priorities",
            "confidence": 0.0,
            "reasoning":  f"Agent failed to respond. Error: {error}",
            "agent_logs": {
                "schedule":   "Agent unavailable",
                "logistics":  "Agent unavailable",
                "preference": "Agent unavailable",
            },
        }
