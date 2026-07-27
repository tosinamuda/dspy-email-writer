"""The task contract.

Every name in here is prompt text. DSPy renders the class docstring as the
instruction and the field names as the labels the model reads and writes, so
`topic` and `tone` do work that `input_1` and `input_2` would not.
"""

import dspy


class WriteEmail(dspy.Signature):
    """Write a professional email about the given topic, in the given tone."""

    topic: str = dspy.InputField(desc="what the email is about")
    tone: str = dspy.InputField(desc="e.g. formal, friendly, urgent")

    subject: str = dspy.OutputField(desc="Email subject line")
    body: str = dspy.OutputField(desc="Full email body")
