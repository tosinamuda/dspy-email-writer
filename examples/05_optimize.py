"""Compile the email writer against the eval set with GEPA.

GEPA runs the program over the eval set, reads what the metric said about each
failure, and has the reflection model rewrite the instruction. It prints the
before and after so the run has a verdict.

    uv run python examples/05_optimize.py
"""

import dspy

from email_writer.config import (
    COMPILED_PATH,
    GEPA_AUTO,
    MAX_METRIC_CALLS,
    NUM_THREADS,
)
from email_writer.data import load_eval_set
from email_writer.lm import reflection_lm, task_lm
from email_writer.metric import email_quality
from email_writer.signature import WriteEmail

if __name__ == "__main__":
    dspy.configure(lm=task_lm())

    eval_set = load_eval_set()
    print(f"Loaded {len(eval_set)} examples")

    email = dspy.ChainOfThought(WriteEmail)
    evaluate = dspy.Evaluate(
        devset=eval_set, metric=email_quality, num_threads=NUM_THREADS
    )

    baseline = evaluate(email)
    print(f"Baseline: {baseline.score:.1f}")

    budget = (
        {"max_metric_calls": MAX_METRIC_CALLS}
        if MAX_METRIC_CALLS
        else {"auto": GEPA_AUTO}
    )
    optimizer = dspy.GEPA(
        metric=email_quality,
        reflection_lm=reflection_lm(),
        num_threads=NUM_THREADS,
        **budget,
    )
    compiled = optimizer.compile(email, trainset=eval_set)

    tuned = evaluate(compiled)
    print(f"Compiled: {tuned.score:.1f} (baseline was {baseline.score:.1f})")

    compiled.save(COMPILED_PATH)
    print(f"Saved to {COMPILED_PATH}")
