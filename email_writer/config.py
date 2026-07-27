"""Where the models and budgets are chosen.

Only two things here are genuinely environmental: which provider you are pointed
at, and your API key. Everything else is a decision about the program, so it
lives in version control where a diff can show it changing.

Set LLM_PROVIDER=ollama to run the whole repo against a local model.
"""

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL_SET_PATH = ROOT / "data" / "email_examples.csv"
COMPILED_PATH = ROOT / "optimized_email_writer.json"


@dataclass(frozen=True)
class Provider:
    """One place to point every script at the same models.

    The DSPy fields and the OpenAI fields describe the same endpoint twice
    because example 01 calls the OpenAI SDK directly, before DSPy exists.
    """

    task_model: str
    reflection_model: str
    api_base: str | None
    openai_model: str
    openai_base_url: str | None
    api_key: str


PROVIDERS = {
    "openai": Provider(
        task_model="openai/gpt-5",
        reflection_model="openai/gpt-5",
        api_base=None,
        openai_model="gpt-5",
        openai_base_url=None,
        api_key=os.getenv("OPENAI_API_KEY", ""),
    ),
    "ollama": Provider(
        task_model="ollama_chat/qwen2.5:7b-instruct",
        reflection_model="ollama_chat/qwen2.5:7b-instruct",
        api_base="http://localhost:11434",
        openai_model="qwen2.5:7b-instruct",
        openai_base_url="http://localhost:11434/v1",
        api_key="ollama",  # ollama accepts any non-empty key
    ),
}


def provider() -> Provider:
    name = os.getenv("LLM_PROVIDER", "openai")
    if name not in PROVIDERS:
        raise SystemExit(
            f"LLM_PROVIDER={name!r} is not one of {sorted(PROVIDERS)}."
        )
    return PROVIDERS[name]


# GEPA's search budget. auto="light" is the one to use for real; set
# MAX_METRIC_CALLS to an int for a short, cheap run while wiring things up.
GEPA_AUTO = "light"
MAX_METRIC_CALLS: int | None = None

NUM_THREADS = 4

# The reflection model rewrites instructions, so it gets room to think.
REFLECTION_TEMPERATURE = 1.0
REFLECTION_MAX_TOKENS = 32000
