"""The choices the examples share. Edit them here, not in the environment.

DSPy talks to every provider through LiteLLM, so the model string *is* the
routing: the prefix picks the backend and LiteLLM finds the key. Nothing here
needs its own idea of a provider.

    openai/gpt-5                     OpenAI, key from OPENAI_API_KEY
    anthropic/claude-sonnet-5        Anthropic, key from ANTHROPIC_API_KEY
    ollama_chat/qwen2.5:7b-instruct  a local ollama server, no key

To run everything locally, swap the four values below for the commented ones.
"""

from pathlib import Path

TASK_MODEL = "openai/gpt-5"
REFLECTION_MODEL = "openai/gpt-5"
API_BASE: str | None = None

# Example 01 runs before DSPy exists, so it names its model the OpenAI SDK way.
OPENAI_MODEL = "gpt-5"

# Local, through ollama:
# TASK_MODEL = "ollama_chat/qwen2.5:7b-instruct"
# REFLECTION_MODEL = "ollama_chat/qwen2.5:7b-instruct"
# API_BASE = "http://localhost:11434"
# OPENAI_MODEL = "qwen2.5:7b-instruct"

ROOT = Path(__file__).resolve().parents[2]
EVAL_SET_PATH = ROOT / "data" / "email_examples.csv"
COMPILED_PATH = ROOT / "optimized_email_writer.json"

# GEPA's search budget. auto="light" is the one to use for real; set
# MAX_METRIC_CALLS to an int for a short, cheap run while wiring things up.
GEPA_AUTO = "light"
MAX_METRIC_CALLS: int | None = None

NUM_THREADS = 4

# The reflection model rewrites instructions, so it gets room to think.
REFLECTION_TEMPERATURE = 1.0
REFLECTION_MAX_TOKENS = 32000
