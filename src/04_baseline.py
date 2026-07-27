"""Score the program before anything is tuned.

Without this number, a compiled program is just a different prompt, not a
better one. Run it before you migrate anything, and run it again after.

    uv run python examples/04_baseline.py
"""

import dspy

from config import NUM_THREADS
from eval_set import load_eval_set
from lm import task_lm
from metric import email_quality
from signature import WriteEmail

if __name__ == "__main__":
    dspy.configure(lm=task_lm())

    eval_set = load_eval_set()
    email = dspy.ChainOfThought(WriteEmail)

    result = dspy.Evaluate(
        devset=eval_set, metric=email_quality, num_threads=NUM_THREADS
    )(email)
    print(f"Baseline over {len(eval_set)} examples: {result.score:.1f}")
