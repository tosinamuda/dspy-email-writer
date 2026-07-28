"""The starting point: one f-string, and the plumbing it needs to survive.

    uv run python examples/01_without_dspy.py
"""

import json

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# The only example that wires up a client by hand. From 02 on, DSPy does it.
client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)


def generate_email(topic: str, tone: str) -> dict:
    prompt = f"""Write a professional email.

Topic: {topic}
Tone: {tone}

Return your response as valid JSON with no markdown formatting:
{{ "subject": "...", "body": "..." }}

Do not include backticks. Do not add text before or after the JSON."""

    for attempt in range(3):
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        try:
            result = json.loads(text)
            assert "subject" in result and "body" in result
            return result
        except (json.JSONDecodeError, AssertionError):
            if attempt == 2:
                raise


if __name__ == "__main__":
    result = generate_email(topic="Following up on a job application", tone="formal")
    print(f"Subject: {result['subject']}")
    print(f"Body: {result['body']}")
