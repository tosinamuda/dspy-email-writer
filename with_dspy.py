"""Email generation with DSPy — the Signature approach."""

import dspy

from lm import task_lm


class WriteEmail(dspy.Signature):
    """Write a professional email about the given topic, in the given tone."""

    topic: str = dspy.InputField(desc="what the email is about")
    tone: str = dspy.InputField(desc="e.g. formal, friendly, urgent")

    subject: str = dspy.OutputField(desc="Email subject line")
    body: str = dspy.OutputField(desc="Full email body")


dspy.configure(lm=task_lm())

email = dspy.ChainOfThought(WriteEmail)

if __name__ == "__main__":
    result = email(topic="Following up on a job application", tone="formal")
    print(f"Subject: {result.subject}")
    print(f"Body: {result.body}")
