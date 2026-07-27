# dspy-email-writer

Companion code for [Stop Hand-Writing and Brute-Forcing Prompts: Use DSPy Instead](https://www.tosinamuda.com/blog/stop-hand-writing-prompts-dspy.html).

One task, generating a professional email, written twice: once as an f-string with the plumbing it needs, once as a DSPy Signature. Then scored, optimized, and loaded back.

## Setup

```bash
uv sync
cp .env.example .env
```

Then pick a provider.

**Against OpenAI**, put your key in `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Against a local model**, no key needed. Install [ollama](https://ollama.com), then:

```bash
ollama pull qwen2.5:7b-instruct
```

```
LLM_PROVIDER=ollama
```

Every script reads the same provider, so this is the only switch. Model names, budgets, and thresholds live in `email_writer/config.py` rather than the environment: they are decisions about the program, and a diff should show them changing.

## Run them in order

```bash
uv run python examples/01_without_dspy.py     # f-string, JSON parsing, retry loop
uv run python examples/02_with_dspy.py        # the same task as a Signature
uv run python examples/03_make_eval_set.py    # invent eval inputs if you have none
uv run python examples/04_baseline.py         # score before tuning anything
uv run python examples/05_optimize.py         # compile with GEPA, print before and after
uv run python examples/06_use_compiled.py     # load the tuned program and call it
```

`01` and `02` do the same job, so read them side by side. `04` is the one people skip; without it, `05` produces a different prompt rather than a better one.

On `qwen2.5:7b-instruct`, `04` scores 66.7 and `05` takes it to 85.4. Most of that gap is the placeholder check: rather than write around a detail it was never given, a small model leaves `[Your Name]` and `[Company]` for a human to fill in.

## Layout

```
email_writer/          # the shared pieces the examples import
  config.py            # providers, models, budgets, paths
  lm.py                # builds the dspy.LM objects
  signature.py         # WriteEmail: the task contract
  metric.py            # what "a good email" means, in code
  data.py              # load the eval set, or invent one
examples/              # numbered, meant to be read in order
data/                  # the eval set: inputs only, no gold answers
skills/prompt-to-dspy/ # a Claude agent skill for migrating your own prompts
```

The eval set has no expected outputs. The metric judges what comes back against rules, so nothing here waits on someone labelling a corpus first.

## Prompt to DSPy skill

`skills/prompt-to-dspy/` converts your own code the way `01` becomes `02`: it finds the f-string prompts, measures a baseline first (inventing eval inputs if the project has none), extracts each contract, proposes a Signature and a module, and scores the result against the number it started with.

It is a migration tool, so install it into the project you are converting rather than globally:

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/prompt-to-dspy /path/to/your-project/.claude/skills/
```

Then ask Claude to convert your prompts. It proposes a before and after per call site; it does not rewrite anything on its own.
