# Prompt to DSPy

Migrate hardcoded LLM prompt templates into DSPy Signatures and Modules.

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

## Step 2: Extract the contract from each prompt

For each prompt found, identify three things:

**Inputs** — the variables injected into the template. These are f-string variables, `.format()` arguments, or concatenated strings. Each one becomes a `dspy.InputField()`. Use the variable name as the field name. Infer the type from usage (usually `str`, but could be `int`, `list[str]`, etc.).

**Outputs** — what the prompt asks the model to return. Look for JSON schemas in the prompt, parsing code after the API call, or field access on the response. Each distinct output field becomes a `dspy.OutputField()`. If the prompt says "return JSON with keys subject and body," those are two output fields.

**Intent** — the core instruction, stripped of formatting rules, JSON instructions, and retry-related text. This becomes the Signature's docstring. It should read as a one-sentence task description: "Write a professional email" not "Return valid JSON with no markdown."

## Step 3: Generate the Signature

Write a DSPy Signature class for each prompt:

```python
class <TaskName>(dspy.Signature):
    """<intent — one sentence describing what this call does>"""

    <input_name>: <type> = dspy.InputField()          # add desc= if the name is ambiguous
    <input_name>: <type> = dspy.InputField()

    <output_name>: <type> = dspy.OutputField()         # add desc= if the name is ambiguous
    <output_name>: <type> = dspy.OutputField()
```

Naming rules:
- Class name describes the task: `WriteEmail`, `SummarizeArticle`, `ClassifyTicket`, `ExtractEntities`
- Field names match the domain, not the implementation: `topic` not `input_3`
- Add `desc=` only when the field name alone would be ambiguous to the model

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

## Step 4: Choose the Module

Match the original prompt's reasoning pattern to a DSPy Module:

| Original pattern | DSPy Module |
|---|---|
| Simple prompt, no reasoning steps | `dspy.Predict(Signature)` |
| "Think step by step," multi-step reasoning, or chain of thought | `dspy.ChainOfThought(Signature)` |
| Uses tools, APIs, or external lookups mid-prompt | `dspy.ReAct(Signature, tools=[...])` |
| Iterates on its own output or has self-critique | `dspy.Refine(Signature)` |

When in doubt, start with `dspy.Predict`. The user can upgrade to `ChainOfThought` later if output quality needs improvement.

## Step 5: Identify removable plumbing

For each converted prompt, list the code that DSPy now handles and that can be removed:

- Prompt template construction (f-strings, `.format()`, string concatenation)
- JSON formatting instructions in the prompt ("Return valid JSON", "Do not include backticks")
- Output parsing (JSON parsing, regex extraction, markdown fence stripping)
- Retry loops for malformed output
- Type validation / assertion checks on the parsed result
- Model-specific formatting (system message construction, role assignment)

## Step 6: Write the migration

Create a new file (e.g. `signatures.py`) containing all generated Signatures. For each original call site, show:

1. The original code (commented or in a docstring for reference)
2. The new DSPy Signature
3. The Module wrapper
4. Which lines of plumbing can be deleted

Present this as a clear before/after so the user can review each conversion and verify the contract is correct before applying it.

## Important

- Do not guess at the output structure. Read the parsing code to confirm what fields the original code expects.
- Preserve any validation logic that is domain-specific (not just "is this valid JSON"). Domain checks become part of the metric function, not the Signature.
- If a prompt template has conditional sections (different instructions based on input), that may need multiple Signatures or a Module with branching logic. Flag this for the user rather than silently collapsing it into one Signature.
- If the original code calls multiple LLMs in sequence (pipeline), each call becomes its own Signature. The pipeline becomes a `dspy.Module` subclass with a `forward()` method that chains them.
