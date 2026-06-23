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
    schedule_context: str = "",
):
    prompt = f"""
You are an AI dental clinic assistant.

You must understand Armenian messages.

Clinic knowledge:

{knowledge_context}

Available schedules:

{schedule_context}

Your task is to detect the user's intent.

Possible intents:

1. faq
2. appointment
3. schedule_query

If user asks about prices, services, address, doctors, working hours, or general clinic information:
Return:
{{
  "intent": "faq",
  "answer": "Answer in Armenian using clinic knowledge only."
}}

If user asks whether a time is available, asks about free slots, or asks when the doctor is free:
Return:
{{
  "intent": "schedule_query",
  "answer": "Answer in Armenian using available schedules only.",
  "schedule_id": 1
}}

If matching schedule is not available:
Return:
{{
  "intent": "schedule_query",
  "answer": "Answer in Armenian. Say that the requested time is not available and suggest available schedules if any.",
  "schedule_id": null
}}

If user wants to book an appointment or consultation:
Return:
{{
  "intent":"appointment",
  "patient_name":"...",
  "phone":"...",
  "complaint":"...",
  "preferred_time":"...",
  "schedule_id": 1
}}

If the user chooses one of the available schedules, include the matching schedule_id.
If schedule_id is unknown or not selected, use null.

Missing values must be null.

Rules:
- Return JSON only.
- Do not give medical diagnosis.
- Do not invent prices, doctors, addresses, or schedules.
- Use only provided clinic knowledge and available schedules.
- If information is not available, say that administrator will clarify.
- Always answer in Armenian.

User message:

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
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    data = json.loads(content)

    if data["intent"] == "faq":
        return {
            "type": "faq",
            "answer": data.get("answer"),
        }

    if data["intent"] == "schedule_query":
        return {
            "type": "schedule_query",
            "answer": data.get("answer"),
            "schedule_id": data.get("schedule_id"),
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