# dspy-email-writer

Companion code for [Stop Hand-Writing and Brute-Forcing Prompts: Use DSPy Instead](https://www.tosinamuda.com/blog/stop-hand-writing-prompts-dspy.html).

One task, generating a professional email, written twice: once as an f-string with the plumbing it needs, once as a DSPy Signature. Then given a metric, scored, optimized, and loaded back.

Follow the steps below in order and you will end up with a prompt you did not write and a number that says it is better than the one you started with.

## Prerequisites

**1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Pick a model.** Either a local one (free, no key) or OpenAI.

For local, install [ollama](https://ollama.com/download), then pull the model these examples were written against:

```bash
ollama pull qwen2.5:7b-instruct
```

Check it is there and the server is up:

```bash
ollama list
curl -s localhost:11434/api/tags | head -c 80
```

A 7B model is small enough to be wrong in interesting ways. That is the point: it is what makes the optimizer's improvement visible.

For OpenAI instead:

```bash
export OPENAI_API_KEY=sk-...
```

**3. Install the dependencies.**

```bash
git clone https://github.com/tosinamuda/dspy-email-writer
cd dspy-email-writer
uv sync
```

**4. Point it at your model.** `src/config.py` defaults to OpenAI. For ollama, replace the four values at the top with the commented block underneath them:

```python
TASK_MODEL = "ollama_chat/qwen2.5:7b-instruct"
REFLECTION_MODEL = "ollama_chat/qwen2.5:7b-instruct"
API_BASE = "http://localhost:11434"
OPENAI_MODEL = "qwen2.5:7b-instruct"
```

That is the only edit you need. DSPy routes through LiteLLM, so the model string picks the backend.

## Step 1: See what you are replacing

```bash
uv run python src/01_without_dspy.py
```

An f-string with formatting rules, a JSON parser, a retry loop, markdown fence stripping, and a manual key check. It works. Note how much of the file is not the task.

## Step 2: Declare the task instead

```bash
uv run python src/02_with_dspy.py
```

Same output, and the prompt is gone. `src/signature.py` is the whole contract: two inputs, two outputs, one sentence of intent. The script ends with `dspy.inspect_history(n=1)`, so you can read the prompt DSPy generated from it.

Read `01` and `02` side by side. That comparison is the point of the repo.

Both will probably hand you an email full of `[Your Name]` and `[Company Name]`. That is the failure the next steps measure and fix.

## Step 3: Get something to measure against

```bash
uv run python src/03_make_eval_set.py
```

Writes twelve rows to `src/data/email_examples.csv`. The repo ships a set already, so this overwrites it; run it to see where an eval set comes from when you do not have one.

The rows are **inputs only**. There are no gold answers anywhere in this repo. `src/metric.py` judges what the model returns against rules, which is why you do not have to write twelve perfect emails first.

## Step 4: Score it before you change anything

```bash
uv run python src/04_baseline.py
```

Expect around **66.7** on `qwen2.5:7b-instruct`. Most of what it is deducting is the placeholder check.

Do not skip this. Without a number from before, a compiled program is just a different prompt rather than a better one.

## Step 5: Let the optimizer write the prompt

```bash
uv run python src/05_optimize.py
```

GEPA runs the program over the eval set, reads what the metric said about each failure, and has the reflection model rewrite the instruction. It prints the baseline and the compiled score, then saves to `optimized_email_writer.json`.

**This takes several minutes against a local model.** Start it and go and do something else. For a quick smoke run instead, set `MAX_METRIC_CALLS = 15` in `src/config.py` — enough to prove the wiring, not enough to improve anything.

## Step 6: Ship the compiled program

```bash
uv run python src/06_use_compiled.py
```

Loads the saved program and calls it. It prints the instruction length before and after loading, which is the clearest way to see that the tuning is real: a one-line docstring becomes a few thousand characters of instruction that GEPA wrote, not you.

The module you started with has none of that in it, which is why production loads the artifact rather than calling the module directly.

## Layout

```
src/
  01_without_dspy.py     f-string, JSON parsing, retry loop
  02_with_dspy.py        the same task as a Signature
  03_make_eval_set.py    invent eval inputs when you have none
  04_baseline.py         score before tuning
  05_optimize.py         compile with GEPA
  06_use_compiled.py     load the tuned program and call it
  config.py              models, budgets, thresholds, paths
  lm.py                  builds the two dspy.LM objects
  signature.py           WriteEmail: the task contract
  metric.py              what "a good email" means, in code
  eval_set.py            load the eval set, or invent one
  data/                  the eval set: inputs only
skills/prompt-to-dspy/   a Claude agent skill for migrating your own prompts
```

Flat on purpose. The scripts run from `src/`, so `src/` is on the import path and `from signature import WriteEmail` works with no install step, no package name, and no `PYTHONPATH`.

Models, search budget, and metric thresholds live in `config.py` rather than the environment: they are decisions about the program, not facts about your machine, so a diff should show them changing. Your API key stays in the environment, where LiteLLM finds it on its own.

## Prompt to DSPy skill

`skills/prompt-to-dspy/` does to your code what steps 1 through 6 do here: finds the f-string prompts, measures a baseline first (inventing eval inputs if your project has none), extracts each contract, proposes a Signature and a module, and scores the result against the number it started with.

It is a migration tool, so install it into the project you are converting rather than globally:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/prompt-to-dspy /path/to/your-project/.claude/skills/
```

Then ask Claude to convert your prompts. It proposes a before and after per call site; it does not rewrite anything on its own.
