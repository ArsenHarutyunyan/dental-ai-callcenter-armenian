import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def build_knowledge_context(items):
    if not items:
        return "No clinic knowledge"

    parts = []

    for item in items:
        parts.append(
            f"""
Category: {item.category}
Title: {item.title}
Content: {item.content}
"""
        )

    return "\n".join(parts)


def process_message(
    user_message: str,
    knowledge_context: str = "",
):
    prompt = f"""
You are an AI dental clinic assistant.

Clinic knowledge:

{knowledge_context}

Your task:

Detect intent.

Possible intents:

1. faq
2. appointment

If user is asking:
- prices
- doctors
- services
- address
- schedule

Return:

{{
    "intent":"faq",
    "answer":"..."
}}

If user wants appointment or consultation:

Return:

{{
    "intent":"appointment",
    "patient_name":"...",
    "phone":"...",
    "complaint":"...",
    "preferred_time":"..."
}}

Missing values must be null.

Return JSON only.

User:

{user_message}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        },
    )

    content = response.choices[0].message.content

    data = json.loads(content)

    if data["intent"] == "faq":
        return {
            "type": "faq",
            "answer": data["answer"],
        }

    missing = []

    if not data.get("patient_name"):
        missing.append("name")

    if not data.get("phone"):
        missing.append("phone")

    if not data.get("preferred_time"):
        missing.append("time")

    return {
        "type": "appointment",
        "ready": len(missing) == 0,
        "missing": missing,
        "data": data,
    }