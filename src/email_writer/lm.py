"""The two models, built from config."""

import dspy

from email_writer.config import (
    API_BASE,
    REFLECTION_MAX_TOKENS,
    REFLECTION_MODEL,
    REFLECTION_TEMPERATURE,
    TASK_MODEL,
)


def _lm(model: str, **kwargs) -> dspy.LM:
    if API_BASE:
        kwargs["api_base"] = API_BASE
    return dspy.LM(model, **kwargs)


def task_lm() -> dspy.LM:
    """The model that writes the emails."""
    return _lm(TASK_MODEL)


def reflection_lm() -> dspy.LM:
    """The model GEPA uses to rewrite instructions. Worth making this a strong
    one: it runs once per proposal, not once per example."""
    return _lm(
        REFLECTION_MODEL,
        temperature=REFLECTION_TEMPERATURE,
        max_tokens=REFLECTION_MAX_TOKENS,
    )
