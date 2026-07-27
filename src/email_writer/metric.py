"""What "a good email" means, in code.

The same function feeds dspy.Evaluate and GEPA. Evaluate reads the score; GEPA
reads the score and the feedback, and hands that text to its reflection model,
so the sentences here are what drive the next instruction rewrite. A bare float
gives it nothing to act on.

Each check is a specific way these outputs have actually gone wrong, not a
general idea of quality. When you meet a new failure, add a check.
"""

import re

import dspy

SUBJECT_MAX_CHARS = 60
BODY_MIN_CHARS = 40

# "[Your Name]", "[Company]", "[insert date]" — the gap a model leaves when it
# does not know something and will not say so.
PLACEHOLDER = re.compile(r"\[[^\]\n]{2,40}\]")

CHECKS = 4


def email_quality(example, prediction, trace=None, pred_name=None, pred_trace=None):
    problems = []

    if len(prediction.subject) > SUBJECT_MAX_CHARS:
        problems.append(
            f"Subject is {len(prediction.subject)} characters. "
            f"Keep it under {SUBJECT_MAX_CHARS}."
        )

    if example.tone.lower() in prediction.body.lower():
        problems.append(
            f"The body names the tone ('{example.tone}') instead of reading that way."
        )

    if len(prediction.body) < BODY_MIN_CHARS:
        problems.append("The body is too short to be a real email.")

    holes = PLACEHOLDER.findall(prediction.body)
    if holes:
        problems.append(
            f"The body leaves blanks for someone to fill in ({', '.join(holes[:3])}). "
            "Write around anything you were not given instead of inventing a slot for it."
        )

    return dspy.Prediction(
        score=1.0 - len(problems) / CHECKS,
        feedback=" ".join(problems) or None,
    )
