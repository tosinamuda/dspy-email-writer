"""Builds the dspy.LM objects from config.py."""

import dspy

from email_writer.config import (
    REFLECTION_MAX_TOKENS,
    REFLECTION_TEMPERATURE,
    provider,
)


def _lm(model: str, **kwargs) -> dspy.LM:
    p = provider()
    if p.api_base:
        kwargs["api_base"] = p.api_base
    return dspy.LM(model, **kwargs)


def task_lm() -> dspy.LM:
    """The model that writes the emails."""
    return _lm(provider().task_model)


def reflection_lm() -> dspy.LM:
    """The model GEPA uses to rewrite instructions. Worth making this a strong
    one: it runs once per proposal, not once per example."""
    return _lm(
        provider().reflection_model,
        temperature=REFLECTION_TEMPERATURE,
        max_tokens=REFLECTION_MAX_TOKENS,
    )
