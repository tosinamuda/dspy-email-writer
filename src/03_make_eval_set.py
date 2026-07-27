"""Invent an eval set when you do not have one.

Optimizing needs inputs to run against, and a migration usually starts with
none. These are inputs only: the metric in 04 judges the output, so no one has
to write gold emails first.

Treat the result as a starter set. Read it, throw out the bland rows, and add a
row every time you meet a failure in the wild.

    uv run python examples/03_make_eval_set.py
"""

import dspy

from config import EVAL_SET_PATH
from eval_set import save_eval_set, synthesize_eval_set
from lm import task_lm

SETTING = "a software company, written by an engineer to colleagues and outside contacts"
COUNT = 12

if __name__ == "__main__":
    dspy.configure(lm=task_lm())

    rows = synthesize_eval_set(setting=SETTING, count=COUNT)
    for row in rows:
        print(f"  {row['tone']:12} {row['topic']}")

    save_eval_set(rows)
    print(f"\nWrote {len(rows)} rows to {EVAL_SET_PATH}")
