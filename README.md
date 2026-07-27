# dspy-email-writer

Companion code for [Stop Hand-Writing and Brute-Forcing Prompts: Use DSPy Instead](https://www.tosinamuda.com/blog/stop-hand-writing-prompts-dspy.html).

One task, generating a professional email, written twice: once as an f-string with the plumbing it needs, once as a DSPy Signature. Then scored, optimized, and loaded back.

## Prerequisites

[uv](https://docs.astral.sh/uv/), and a model to talk to. Pick one.

**A local model, no API key.** Install [ollama](https://ollama.com/download), then pull the model these examples were written against:

```bash
ollama pull qwen2.5:7b-instruct
```

`ollama serve` runs in the background once installed; `ollama list` confirms the model is there. A 7B model is small enough to be wrong in interesting ways, which is the point: it is what makes the optimizer's improvement visible.

**Or OpenAI:**

```bash
export OPENAI_API_KEY=sk-...
```

## Setup

```bash
uv sync
```

The examples default to OpenAI. To run locally instead, swap the four values at the top of `src/email_writer/config.py` for the commented ollama block underneath them.

That file is where the models, the search budget, and the metric thresholds live. They are decisions about the program rather than facts about your machine, so they sit in version control where a diff shows them changing. The one thing left in the environment is your API key, which LiteLLM reads on its own.

## Run them in order

```bash
uv run python src/examples/01_without_dspy.py     # f-string, JSON parsing, retry loop
uv run python src/examples/02_with_dspy.py        # the same task as a Signature
uv run python src/examples/03_make_eval_set.py    # invent eval inputs if you have none
uv run python src/examples/04_baseline.py         # score before tuning anything
uv run python src/examples/05_optimize.py         # compile with GEPA, print before and after
uv run python src/examples/06_use_compiled.py     # load the tuned program and call it
```

`01` and `02` do the same job, so read them side by side. `04` is the one people skip; without it, `05` produces a different prompt rather than a better one.

On `qwen2.5:7b-instruct`, `04` scores 66.7. Most of what it is catching is the placeholder check: rather than write around a detail it was never given, a small model leaves `[Your Name]` and `[Company]` for a human to fill in. `05` takes several minutes against a local model, so start it and go and do something else.

## Layout

```
src/
  email_writer/          # the package the examples import
    config.py            # models, budgets, thresholds, paths
    lm.py                # builds the two dspy.LM objects
    signature.py         # WriteEmail: the task contract
    metric.py            # what "a good email" means, in code
    data.py              # load the eval set, or invent one
  examples/              # numbered, meant to be read in order
  data/                  # the eval set: inputs only, no gold answers
skills/prompt-to-dspy/   # a Claude agent skill for migrating your own prompts
```

The examples are scripts rather than an importable package, because a Python module name cannot start with a digit and the numbering is worth more than the import.

The eval set has no expected outputs. The metric judges what comes back against rules, so nothing here waits on someone labelling a corpus first.

## Prompt to DSPy skill

`skills/prompt-to-dspy/` converts your own code the way `01` becomes `02`: it finds the f-string prompts, measures a baseline first (inventing eval inputs if the project has none), extracts each contract, proposes a Signature and a module, and scores the result against the number it started with.

It is a migration tool, so install it into the project you are converting rather than globally:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/prompt-to-dspy /path/to/your-project/.claude/skills/
```

Then ask Claude to convert your prompts. It proposes a before and after per call site; it does not rewrite anything on its own.
