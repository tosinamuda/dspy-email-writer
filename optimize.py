"""Compile the email writer from an eval set using GEPA."""

import os
import re

import pandas as pd

import dspy
from lm import reflection_lm, task_lm
from with_dspy import WriteEmail

# "[Your Name]", "[Company]", "[insert date]" — the gap a model leaves when it
# does not know something and will not say so.
PLACEHOLDER = re.compile(r"\[[^\]\n]{2,40}\]")

CHECKS = 4


def email_quality(example, prediction, trace=None, pred_name=None, pred_trace=None):
    """Score an email and say what is wrong with it.

    GEPA hands the feedback string to its reflection model, so this text is what
    drives the next instruction rewrite. A bare score gives it nothing to act on.
    """
    problems = []

    if len(prediction.subject) > 60:
        problems.append(f"Subject is {len(prediction.subject)} characters. Keep it under 60.")

    if example.tone.lower() in prediction.body.lower():
        problems.append(f"The body names the tone ('{example.tone}') instead of reading that way.")

    if len(prediction.body) < 40:
        problems.append("The body is too short to be a real email.")

    holes = PLACEHOLDER.findall(prediction.body)
    if holes:
        shown = ", ".join(holes[:3])
        problems.append(
            f"The body leaves blanks for someone to fill in ({shown}). "
            "Write around anything you were not given instead of inventing a slot for it."
        )

    return dspy.Prediction(
        score=1.0 - len(problems) / CHECKS,
        feedback=" ".join(problems) or None,
    )


def load_eval_set(path: str = "email_examples.csv") -> list[dspy.Example]:
    df = pd.read_csv(path)
    return [
        dspy.Example(**row).with_inputs("topic", "tone")
        for row in df.to_dict("records")
    ]


if __name__ == "__main__":
    dspy.configure(lm=task_lm())

    eval_set = load_eval_set()
    print(f"Loaded {len(eval_set)} examples")

    email = dspy.ChainOfThought(WriteEmail)

    baseline = dspy.Evaluate(devset=eval_set, metric=email_quality, num_threads=4)(email)
    print(f"Baseline: {baseline.score:.1f}")

    # auto="light" is the search budget to use for real. Set GEPA_MAX_METRIC_CALLS
    # for a short, cheap run while you are still wiring things up.
    budget = (
        {"max_metric_calls": int(os.environ["GEPA_MAX_METRIC_CALLS"])}
        if "GEPA_MAX_METRIC_CALLS" in os.environ
        else {"auto": "light"}
    )

    optimizer = dspy.GEPA(
        metric=email_quality,
        reflection_lm=reflection_lm(),
        num_threads=4,
        **budget,
    )
    compiled_email = optimizer.compile(email, trainset=eval_set)

    tuned = dspy.Evaluate(devset=eval_set, metric=email_quality, num_threads=4)(compiled_email)
    print(f"Compiled: {tuned.score:.1f} (baseline was {baseline.score:.1f})")

    compiled_email.save("optimized_email_writer.json")
    print("Saved compiled program to optimized_email_writer.json")
