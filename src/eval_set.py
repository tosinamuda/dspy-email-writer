"""Loading the eval set, and inventing one when you do not have it yet.

The eval set is inputs only. Nothing here is a gold answer: the metric judges
the model's output against rules, so migrating an existing prompt does not wait
on anyone labelling a corpus first.
"""

import csv

import dspy
from pydantic import BaseModel, Field

from config import EVAL_SET_PATH

INPUT_FIELDS = ("topic", "tone")


def load_eval_set(path=EVAL_SET_PATH) -> list[dspy.Example]:
    with open(path, newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    return [dspy.Example(**row).with_inputs(*INPUT_FIELDS) for row in rows]


def save_eval_set(rows: list[dict], path=EVAL_SET_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(INPUT_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


class EmailTask(BaseModel):
    topic: str = Field(description="what the email is about, as a short phrase")
    tone: str = Field(description="one word, e.g. formal, friendly, urgent, apologetic")


class InventEmailTasks(dspy.Signature):
    """Invent realistic, varied email-writing tasks for testing an email generator.

    Vary the situation and the tone. Include awkward cases: bad news, a chase-up,
    a correction. Do not invent names, companies, or dates.
    """

    setting: str = dspy.InputField(desc="where these emails are written, e.g. a software team")
    count: int = dspy.InputField(desc="how many tasks to invent")

    tasks: list[EmailTask] = dspy.OutputField(desc="one entry per task, no duplicates")


def synthesize_eval_set(setting: str, count: int) -> list[dict]:
    """Ask the model for eval inputs. A starter set to grow, not a finished one."""
    invent = dspy.ChainOfThought(InventEmailTasks)
    tasks = invent(setting=setting, count=count).tasks
    return [{"topic": t.topic, "tone": t.tone} for t in tasks[:count]]
