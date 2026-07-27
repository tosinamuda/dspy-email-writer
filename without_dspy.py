"""Email generation without DSPy — the f-string approach."""

import json

from openai import OpenAI

client = OpenAI()


def generate_email(sender: str, recipient: str, topic: str, tone: str) -> dict:
    prompt = f"""Write a professional email.

From: {sender}
To: {recipient}
Topic: {topic}
Tone: {tone}

Return your response as valid JSON with no markdown formatting:
{{ "subject": "...", "body": "..." }}

Do not include backticks. Do not add text before or after the JSON."""

    for attempt in range(3):
        response = client.chat.completions.create(
            model="gpt-4o",
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
    result = generate_email(
        sender="Tosin",
        recipient="Hiring Manager",
        topic="Application follow-up",
        tone="formal",
    )
    print(f"Subject: {result['subject']}")
    print(f"Body: {result['body']}")
