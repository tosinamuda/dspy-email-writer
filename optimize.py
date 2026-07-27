"""Compile the email writer from an eval set using GEPA."""

import pandas as pd

import dspy
from with_dspy import WriteEmail


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

    return dspy.Prediction(
        score=1.0 - len(problems) / 3,
        feedback=" ".join(problems) or None,
    )


def load_eval_set(path: str = "email_examples.csv") -> list[dspy.Example]:
    df = pd.read_csv(path)
    return [
        dspy.Example(**row).with_inputs("sender", "recipient", "topic", "tone")
        for row in df.to_dict("records")
    ]


if __name__ == "__main__":
    dspy.configure(lm=dspy.LM("openai/gpt-4o"))

    eval_set = load_eval_set()
    print(f"Loaded {len(eval_set)} examples")

    optimizer = dspy.GEPA(
        metric=email_quality,
        auto="light",  # search budget: light, medium, or heavy
        reflection_lm=dspy.LM("openai/gpt-5", temperature=1.0, max_tokens=32000),
        num_threads=4,
    )
    compiled_email = optimizer.compile(
        dspy.ChainOfThought(WriteEmail), trainset=eval_set
    )
    compiled_email.save("optimized_email_writer/", save_program=True)
    print("Saved compiled program to optimized_email_writer/")
