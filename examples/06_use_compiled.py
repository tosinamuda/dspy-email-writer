"""Load the compiled program and call it, which is what production does.

The module you start with has none of the tuning in it. Loading swaps in the
instruction GEPA wrote, and this prints it so you can see what you are shipping.

    uv run python examples/06_use_compiled.py
"""

import dspy

from email_writer.config import COMPILED_PATH
from email_writer.lm import task_lm
from email_writer.signature import WriteEmail

if __name__ == "__main__":
    if not COMPILED_PATH.exists():
        raise SystemExit(f"No compiled program at {COMPILED_PATH}. Run 05_optimize.py first.")

    dspy.configure(lm=task_lm())

    email = dspy.ChainOfThought(WriteEmail)
    before = len(email.predict.signature.instructions)

    email.load(COMPILED_PATH)
    after = email.predict.signature.instructions
    print(f"Instruction: {before} chars before load, {len(after)} after\n")
    print(after[:400] + ("..." if len(after) > 400 else ""))

    result = email(topic="Following up on a job application", tone="formal")
    print(f"\nSubject: {result.subject}")
    print(f"Body: {result.body}")
