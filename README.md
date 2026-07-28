# dspy-email-writer

Companion code for [Stop Hand-Writing and Brute-Forcing Prompts: Use DSPy Instead](https://www.tosinamuda.com/blog/stop-hand-writing-prompts-dspy.html).

One task, written twice:

- **`01_without_dspy.py`** builds a prompt by hand. It needs a JSON parser, a retry loop, and a fence stripper.
- **`02_with_dspy.py`** declares a Signature. It has no prompt.

The other examples add a metric, a baseline, an optimizer, and a compiled prompt.

## Install

```bash
git clone https://github.com/tosinamuda/dspy-email-writer
cd dspy-email-writer
uv sync
cp .env.example .env
```

You need [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Models

Two models do two jobs:

| Job | Default | Runs |
| --- | --- | --- |
| Task | `qwen3:4b` | once per example |
| Reflection | `gpt-oss:20b` | once per GEPA proposal |

Make the reflection model the stronger one. It runs far less often.

For local models, install [ollama](https://ollama.com/download) and pull both:

```bash
ollama pull qwen3:4b       # 2.5 GB
ollama pull gpt-oss:20b    # 13 GB
```

For OpenAI, edit `.env`. The file shows which lines to change.

`.env` overrides `src/config.py`. A real environment variable overrides both.

## Run

Run the examples in order:

```bash
uv run python src/01_without_dspy.py     # the prompt you replace
uv run python src/02_with_dspy.py        # the same task as a Signature
uv run python src/03_make_eval_set.py    # invent eval inputs
uv run python src/04_baseline.py         # score before you tune
uv run python src/05_optimize.py         # compile with GEPA
uv run python src/06_use_compiled.py     # load the tuned program
```

What to look for:

- Read `01` and `02` together. That comparison is the point.
- Both leave `[Your Name]` in the email. Step 4 deducts marks for it.
- `02` ends with `dspy.inspect_history(n=1)`. It prints the generated prompt.
- The eval set holds inputs only. The metric judges the output, so gold answers are not needed.
- Step 4 scores **64.6** on `qwen3:4b`. Write your number down. It is the only proof that step 5 helped.
- Step 5 needs tens of minutes on local models. Start it and do something else.
- Step 6 prints the instruction length before and after the load. A one-line docstring becomes a few thousand characters.

For a short step 5, set `MAX_METRIC_CALLS=40` in `.env`. Keep the value above the eval set size, or GEPA proposes nothing.

## Files

```
src/
  01_without_dspy.py     f-string, JSON parsing, retry loop
  02_with_dspy.py        the same task as a Signature
  03_make_eval_set.py    invent eval inputs
  04_baseline.py         score before tuning
  05_optimize.py         compile with GEPA
  06_use_compiled.py     load the tuned program
  config.py              models, budget, paths
  lm.py                  builds the two dspy.LM objects
  signature.py           the task contract
  metric.py              what a good email is, in code
  eval_set.py            load or invent the eval set
  data/                  the eval set
skills/prompt-to-dspy/   migrate your own prompts
```

The layout is flat. The scripts run from `src/`, so `from signature import WriteEmail` needs no install step and no `PYTHONPATH`.

## Migrate your own prompts

`skills/prompt-to-dspy/` is a Claude agent skill. It does to your code what steps 1 to 6 do here:

1. Find the f-string prompts.
2. Score the code as it stands. It invents eval inputs if your project has none.
3. Propose a Signature and a module for each call.
4. Score the result against the first number.

Install it into the project you convert, not globally:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/prompt-to-dspy /path/to/your-project/.claude/skills/
```

Then ask Claude to convert your prompts. It proposes a before and after for each call site. It changes nothing on its own.
