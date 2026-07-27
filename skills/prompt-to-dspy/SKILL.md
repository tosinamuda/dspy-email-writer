---
name: prompt-to-dspy
description: Migrate hardcoded LLM prompt templates into DSPy Signatures and Modules, with a measured baseline on both sides of the change. Use when converting existing LLM code to DSPy — "convert my prompts to DSPy", "migrate to DSPy", "extract signatures from my code" — or when pointed at a file with f-string prompts, JSON parsing, and retry loops around a model call.
---

# Prompt to DSPy

Migrate hardcoded LLM prompt templates into DSPy Signatures and Modules.

The order matters: measure first, convert second, compare third.

## When to use

The user wants to convert existing LLM code to DSPy. They might say "convert my prompts to DSPy," "migrate to DSPy," "extract signatures from my code," or point to a specific file with hardcoded prompts.

## Step 1: Find the prompts

Search the codebase for hardcoded LLM prompts. Look for these patterns:

```bash
# f-strings or template strings near LLM API calls
grep -rn "f\"\"\"" --include="*.py" .
grep -rn "f'''" --include="*.py" .

# direct API calls
grep -rn "completions.create\|messages.create\|generate\|invoke" --include="*.py" .

# common variable names
grep -rn "prompt\|system_message\|user_message\|template" --include="*.py" .
```

Read each file that matches. Identify each distinct LLM call site: the prompt template, the API call, and any parsing/retry logic around it.

## Step 2: Get a baseline before you change anything

A migration with no number attached to it cannot be reviewed. Whoever reads the
diff has no way to tell an improvement from a rewrite, and neither do you.

**If the project already has eval data, use it.** Look for fixtures, recorded
prompts and responses, a golden-file test directory, or rows in a database.

**If it does not, generate the inputs.** This is the common case, and it is not
a blocker. The eval set needs the *inputs* a call receives, not model answers:

```python
class Case(BaseModel):                       # one field per input the call takes
    topic: str = Field(description="what the email is about")
    tone: str = Field(description="one word, e.g. formal, urgent")

class InventCases(dspy.Signature):
    """Invent realistic, varied inputs for testing <the task>."""
    setting: str = dspy.InputField(desc="where this runs, e.g. a support desk")
    count: int = dspy.InputField()
    cases: list[Case] = dspy.OutputField(desc="no duplicates")

cases = dspy.ChainOfThought(InventCases)(setting=..., count=12).cases
```

A dozen rows is enough to watch a score move. DSPy's own guidance is 30 to 300
examples for training and validation each, so
treat a first batch as a floor to grow, not a target you have hit. Read what
comes back and delete the bland rows. Vary whatever changes what a good answer
looks like, and include the awkward cases the original prompt gets wrong.

**Then write the metric and score the original code.** The metric encodes how
these outputs actually fail, which the existing code often already tells you:
its retry conditions, validation checks, and any bug reports about it are the
first checks to write. Return a score and a sentence, because an optimizer's
reflection step reads the sentence:

```python
return dspy.Prediction(score=..., feedback="what was wrong" or None)
```

Run it against the pre-migration code and keep the number. Ask the user before
spending real API calls on a large eval set.

## Step 3: Extract the contract from each prompt

For each prompt found, identify three things:

**Inputs** — the variables injected into the template. These are f-string variables, `.format()` arguments, or concatenated strings. Each one becomes a `dspy.InputField()`. Use the variable name as the field name. Infer the type from usage (usually `str`, but could be `int`, `list[str]`, etc.).

**Outputs** — what the prompt asks the model to return. Look for JSON schemas in the prompt, parsing code after the API call, or field access on the response. Each distinct output field becomes a `dspy.OutputField()`. If the prompt says "return JSON with keys subject and body," those are two output fields.

**Intent** — the core instruction, stripped of formatting rules, JSON instructions, and retry-related text. This becomes the Signature's docstring. It should read as a one-sentence task description: "Write a professional email" not "Return valid JSON with no markdown."

## Step 4: Generate the Signature

Write a DSPy Signature class for each prompt:

```python
class <TaskName>(dspy.Signature):
    """<intent — one sentence describing what this call does>"""

    <input_name>: <type> = dspy.InputField()          # add desc= if the name is ambiguous
    <input_name>: <type> = dspy.InputField()

    <output_name>: <type> = dspy.OutputField()         # add desc= if the name is ambiguous
    <output_name>: <type> = dspy.OutputField()
```

### Names are prompt text

This is the step people get wrong on the way in. Nothing here is a variable
name that only the compiler sees. DSPy renders the class docstring as the
instruction and the field names as the labels the model reads and writes, so a
Signature is *written for the model*, and a vague name is a vague prompt.

- Class name describes the task: `WriteEmail`, `SummarizeArticle`, `ClassifyTicket`.
- Field names come from the domain, not the code that used to hold them:
  `topic`, not `input_3`, `arg2`, or `cust_msg_raw`. Expand internal
  abbreviations the model has never seen.
- The docstring is the instruction. One sentence saying what the task is. Do
  not paste the old prompt into it: an optimizer rewrites this text later, and
  a bloated seed gets in the way.
- Add `desc=` when the name alone is ambiguous (`tone` earns
  `desc="e.g. formal, friendly, urgent"`). Put constraints here too, in words
  the model can act on, not only in a validator it never sees.

Check the result rather than assuming: `dspy.inspect_history(n=1)` after a call
prints what was actually sent.

If the output is complex (nested dict, list of objects), define a Pydantic model and use it as the output type:

```python
from pydantic import BaseModel

class EmailResult(BaseModel):
    subject: str
    body: str
    priority: Literal["low", "medium", "high"]

class WriteEmail(dspy.Signature):
    """Write a professional email."""
    sender: str = dspy.InputField()
    email: EmailResult = dspy.OutputField()
```

## Step 5: Choose the Module

Match the original prompt's reasoning pattern to a DSPy Module:

| Original pattern | DSPy Module |
|---|---|
| Simple prompt, no reasoning steps | `dspy.Predict(Signature)` |
| "Think step by step," multi-step reasoning, or chain of thought | `dspy.ChainOfThought(Signature)` |
| Uses tools, APIs, or external lookups mid-prompt | `dspy.ReAct(Signature, tools=[...])` |
| Iterates on its own output or has self-critique | `dspy.Refine(Signature)` |
| Reasons over a context too large for one prompt (a long log, a big document) | `dspy.RLM(Signature)` |

When in doubt, start with `dspy.Predict`. The user can upgrade to
`ChainOfThought` later if output quality needs improvement.

`dspy.RLM` is the exception to "start small": it is for the case where the
original code was already chunking, truncating, or map-reducing a context to
fit a window. Instead of a prompt, it writes Python in a sandboxed REPL to
explore the data and calls a `sub_lm` for the semantic parts. It is
experimental and its API may change, so say so when proposing it, and check
that its `max_iterations` and `max_llm_calls` limits suit the task.

## Step 6: Identify removable plumbing

For each converted prompt, list the code that DSPy now handles and that can be removed:

- Prompt template construction (f-strings, `.format()`, string concatenation)
- JSON formatting instructions in the prompt ("Return valid JSON", "Do not include backticks")
- Output parsing (JSON parsing, regex extraction, markdown fence stripping)
- Retry loops for malformed output
- Type validation / assertion checks on the parsed result
- Model-specific formatting (system message construction, role assignment)

## Step 7: Write the migration

Create a new file (e.g. `signatures.py`) containing all generated Signatures. For each original call site, show:

1. The original code (commented or in a docstring for reference)
2. The new DSPy Signature
3. The Module wrapper
4. Which lines of plumbing can be deleted

Present this as a clear before/after so the user can review each conversion and verify the contract is correct before applying it.

## Step 8: Score the migration against the baseline

Run the metric from step 2 against the DSPy version and put the two numbers
next to each other. Three outcomes, and the first is the one to expect:

- **Same score.** The expected result, and a good one. The migration bought
  structure, not quality: the plumbing is gone and the call is now optimizable.
- **Lower.** Something in the contract is wrong. Read the rendered prompt with
  `dspy.inspect_history(n=1)` before touching the Signature. Usually a field
  name means less to the model than the sentence it replaced, or an instruction
  that was carrying real weight got dropped as "formatting".
- **Higher.** Do not claim it yet. A dozen examples move easily; check whether
  the difference survives on rows the metric was not written against.

Then run an optimizer and report that number too, so the user can see what the
migration unlocked rather than taking it on faith. The point was never that DSPy
writes a better prompt today. It is that the score is now something you can
move on purpose.

## Important

- Do not guess at the output structure. Read the parsing code to confirm what fields the original code expects.
- Preserve any validation logic that is domain-specific (not just "is this valid JSON"). Domain checks become part of the metric function, not the Signature.
- If a prompt template has conditional sections (different instructions based on input), that may need multiple Signatures or a Module with branching logic. Flag this for the user rather than silently collapsing it into one Signature.
- If the original code calls multiple LLMs in sequence (pipeline), each call becomes its own Signature. The pipeline becomes a `dspy.Module` subclass with a `forward()` method that chains them.
