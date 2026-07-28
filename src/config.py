"""The choices the examples share. Edit them here, not in the environment.

DSPy talks to every provider through LiteLLM, so the model string *is* the
routing: the prefix picks the backend and LiteLLM finds the key.

    openai/gpt-5                 OpenAI, key from OPENAI_API_KEY
    anthropic/claude-sonnet-5    Anthropic, key from ANTHROPIC_API_KEY
    ollama_chat/qwen3:4b         a local ollama server, no key

Two models, doing different jobs. The task model writes the emails, once per
example. The reflection model rewrites the instruction, once per proposal, so
GEPA gets more out of a stronger model there than it costs you. Point the task
model at something small and cheap and spend on reflection instead.
"""

from pathlib import Path

# Local, through ollama: a 4B writes, a 20B reasoner critiques.
TASK_MODEL = "ollama_chat/qwen3:4b"
REFLECTION_MODEL = "ollama_chat/gpt-oss:20b"
API_BASE: str | None = "http://localhost:11434"

# Hosted, if you would rather spend money than disk:
# TASK_MODEL = "openai/gpt-5-mini"
# REFLECTION_MODEL = "openai/gpt-5"
# API_BASE = None

# Example 01 runs before DSPy exists, so it names the model the OpenAI SDK way,
# without the LiteLLM prefix that picks the backend.
OPENAI_MODEL = TASK_MODEL.split("/", 1)[-1]

SRC = Path(__file__).resolve().parent
EVAL_SET_PATH = SRC / "data" / "email_examples.csv"

# A build output, not source, so it lands at the repo root rather than in src/.
COMPILED_PATH = SRC.parent / "optimized_email_writer.json"

# GEPA's search budget. auto="light" is the one to use for real; set
# MAX_METRIC_CALLS to an int for a short, cheap run while wiring things up.
GEPA_AUTO = "light"
MAX_METRIC_CALLS: int | None = None

NUM_THREADS = 4

# The reflection model rewrites instructions, so it gets room to think.
REFLECTION_TEMPERATURE = 1.0
REFLECTION_MAX_TOKENS = 32000
