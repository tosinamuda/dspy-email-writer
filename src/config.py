"""Defaults for the examples. A .env file overrides them.

DSPy uses LiteLLM. The model string selects the backend:

    openai/gpt-5                 OpenAI. Key from OPENAI_API_KEY.
    anthropic/claude-sonnet-5    Anthropic. Key from ANTHROPIC_API_KEY.
    ollama_chat/qwen3:4b         A local ollama server. No key.

Two models do two jobs. The task model writes each email. The reflection model
rewrites the instruction once per GEPA proposal, not once per example. Make the
reflection model the stronger of the two.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

SRC = Path(__file__).resolve().parent

# Real environment variables win. A .env file fills in the rest.
load_dotenv(SRC.parent / ".env")

TASK_MODEL = os.getenv("TASK_MODEL", "ollama_chat/qwen3:4b")
REFLECTION_MODEL = os.getenv("REFLECTION_MODEL", "ollama_chat/gpt-oss:20b")
API_BASE = os.getenv("API_BASE", "http://localhost:11434") or None

# Example 01 runs before DSPy exists, so it talks to the OpenAI SDK directly.
# The SDK wants the model without the LiteLLM prefix, the /v1 suffix on the
# base URL, and a key even when the server ignores one.
OPENAI_MODEL = TASK_MODEL.split("/", 1)[-1]
OPENAI_BASE_URL = f"{API_BASE}/v1" if API_BASE else None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ("local" if API_BASE else None)

EVAL_SET_PATH = SRC / "data" / "email_examples.csv"

# A build output, not source. It goes to the repo root.
COMPILED_PATH = SRC.parent / "optimized_email_writer.json"

# GEPA's search budget. Use GEPA_AUTO for a real run. Set MAX_METRIC_CALLS
# above the eval set size for a short one, or GEPA proposes nothing.
GEPA_AUTO = os.getenv("GEPA_AUTO", "light")
MAX_METRIC_CALLS = int(os.getenv("MAX_METRIC_CALLS", "0")) or None

NUM_THREADS = int(os.getenv("NUM_THREADS", "4"))

# The reflection model rewrites instructions. Give it room to think.
REFLECTION_TEMPERATURE = 1.0
REFLECTION_MAX_TOKENS = 32000

# Metric thresholds live in metric.py, beside the checks that use them.
