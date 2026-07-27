"""The same task as 01, declared instead of written.

No prompt string, no JSON instructions, no retry loop, no fence stripping. The
result comes back typed.

    uv run python examples/02_with_dspy.py
"""

import dspy

from email_writer.lm import task_lm
from email_writer.signature import WriteEmail

dspy.configure(lm=task_lm())

email = dspy.ChainOfThought(WriteEmail)

if __name__ == "__main__":
    result = email(topic="Following up on a job application", tone="formal")
    print(f"Subject: {result.subject}")
    print(f"Body: {result.body}")

    # What DSPy actually sent, which is the thing worth reading once.
    dspy.inspect_history(n=1)
