import os
from crewai import LLM


def make_llm(model: str):
    """OpenRouter-only LLM via LiteLLM. Only OPENROUTER_API_KEY is used.
    Prefix with openrouter/ so CrewAI uses LiteLLM instead of native SDKs.
    """
    openrouter_model = f"openrouter/{model}" if not model.startswith("openrouter/") else model
    return LLM(
        model=openrouter_model,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.7,
    )
