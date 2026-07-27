"""Email generation with DSPy — the Signature approach."""

import dspy

from lm import task_lm


class WriteEmail(dspy.Signature):
    """Write a professional email for the given sender, recipient, topic, and tone."""

    sender: str = dspy.InputField()
    recipient: str = dspy.InputField()
    topic: str = dspy.InputField()
    tone: str = dspy.InputField(desc="e.g. formal, friendly, urgent")

    subject: str = dspy.OutputField(desc="Email subject line")
    body: str = dspy.OutputField(desc="Full email body")


dspy.configure(lm=task_lm())

email = dspy.ChainOfThought(WriteEmail)

if __name__ == "__main__":
    result = email(
        sender="Tosin",
        recipient="Hiring Manager",
        topic="Application follow-up",
        tone="formal",
    )
    print(f"Subject: {result.subject}")
    print(f"Body: {result.body}")
