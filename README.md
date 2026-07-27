# dspy-email-writer

Companion code for [Can't Get Enough of DSPy](https://www.tosinamuda.com/blog/cant-get-enough-of-dspy).

The same task (generate a professional email) implemented two ways: raw prompt engineering and DSPy. Run both, compare the code, and see what DSPy handles for you.

## Setup

```bash
uv sync
```

## Files

- `without_dspy.py` — f-string prompt with JSON parsing, retry loop, and manual validation
- `with_dspy.py` — DSPy Signature and ChainOfThought module
- `optimize.py` — compile the email writer from an eval set using GEPA
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

The `skills/prompt-to-dspy/` directory contains a Claude agent skill for migrating hardcoded prompt templates to DSPy Signatures. Point it at a codebase and it will scan for f-string prompts, extract the contract (inputs, outputs, intent), and generate Signature classes.
