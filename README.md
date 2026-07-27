# dspy-email-writer

Companion code for [Stop Hand-Writing and Brute-Forcing Prompts: Use DSPy Instead](https://www.tosinamuda.com/blog/stop-hand-writing-prompts-dspy.html).

The same task (generate a professional email) implemented two ways: raw prompt engineering and DSPy. Run both, compare the code, and see what DSPy handles for you.

## Setup

```bash
uv sync
```

## Files

- `without_dspy.py` — f-string prompt with JSON parsing, retry loop, and manual validation
- `with_dspy.py` — DSPy Signature and ChainOfThought module
- `optimize.py` — score a baseline, compile the email writer from the eval set with GEPA, then save the tuned program
- `lm.py` — which model the scripts talk to (defaults to OpenAI; override with env vars)
- `email_examples.csv` — sample eval set (12 rows, one per test case)

## Run

```bash
# Without DSPy
uv run python without_dspy.py

# With DSPy
uv run python with_dspy.py

# Optimize from eval set
uv run python optimize.py
```

## Prompt to DSPy skill

`skills/prompt-to-dspy/` is a Claude agent skill that does the `without_dspy.py` → `with_dspy.py` conversion on your own code: it scans for f-string prompts, extracts the contract (inputs, outputs, intent), picks a module, and lists the plumbing you can then delete.

Install it into the project you want to convert, not globally — it is a migration tool, so it should be present while you migrate and gone afterwards:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/prompt-to-dspy /path/to/your-project/.claude/skills/
```

Then, from that project, ask Claude to convert your prompts to DSPy. It proposes a before/after per call site for you to review; it does not rewrite anything on its own.

## Running against another provider

The scripts default to OpenAI. To use anything else, including a local model, set the model and base URL instead of editing the code:

```bash
# DSPy scripts, against a local ollama model
DSPY_MODEL=ollama_chat/qwen2.5:7b-instruct \
DSPY_API_BASE=http://localhost:11434 \
DSPY_REFLECTION_MODEL=ollama_chat/qwen2.5:7b-instruct \
GEPA_MAX_METRIC_CALLS=25 \
uv run python optimize.py

# the without-DSPy script talks to the OpenAI SDK directly
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama OPENAI_MODEL=qwen2.5:7b-instruct \
uv run python without_dspy.py
```

`GEPA_MAX_METRIC_CALLS` caps the optimizer's search for a quick run. Leave it unset to use the `auto="light"` budget.
