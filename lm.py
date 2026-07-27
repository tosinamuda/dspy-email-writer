"""Which model the scripts talk to.

Defaults to OpenAI, as the article does. Point it anywhere else without editing
the scripts:

    DSPY_MODEL=ollama_chat/qwen2.5:7b-instruct \
    DSPY_API_BASE=http://localhost:11434 \
    uv run python with_dspy.py
"""

import os

import dspy

DEFAULT_MODEL = "openai/gpt-4o"
DEFAULT_REFLECTION_MODEL = "openai/gpt-5"


def _lm(model: str, **kwargs) -> dspy.LM:
    api_base = os.getenv("DSPY_API_BASE")
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)


def task_lm() -> dspy.LM:
    """The model that does the work."""
    return _lm(os.getenv("DSPY_MODEL", DEFAULT_MODEL))


def reflection_lm() -> dspy.LM:
    """The model GEPA uses to rewrite instructions. Worth making this a strong one:
    it runs once per proposal, not once per example."""
    return _lm(
        os.getenv("DSPY_REFLECTION_MODEL", DEFAULT_REFLECTION_MODEL),
        temperature=1.0,
        max_tokens=32000,
    )
