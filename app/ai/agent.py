import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")


def call_local_llm(prompt: str) -> str:
    """Local, fully offline replacement for the Groq call. Same contract:
    takes the full prompt, returns raw JSON text."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False,
            "think": False,  # qwen3 "thinking" mode would pollute JSON output
            "options": {"temperature": 0},
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


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
    patient_context: str = "",
):
    prompt = f"""
You are an AI dental clinic receptionist.

You must understand Armenian messages and always answer in Armenian.

Clinic knowledge:
{knowledge_context}

Available schedules:
{schedule_context}

Patient context:
{patient_context}

Your task is to detect the user's intent.

Possible intents:
1. faq
2. price_query
3. service_query
4. doctor_query
5. working_hours_query
6. schedule_query
7. appointment
8. cancel_appointment
9. reschedule_appointment

If user asks about prices, services, doctors, address, working hours, or clinic information:
Return:
{{
  "intent": "faq",
  "answer": "Answer in Armenian using only clinic knowledge."
}}

If user asks whether a time is available or asks for free slots:
Return:
{{
  "intent": "schedule_query",
  "answer": "Answer in Armenian using only available schedules.",
  "schedule_id": 1
}}

If matching schedule is not available:
Return:
{{
  "intent": "schedule_query",
  "answer": "Answer in Armenian. Say the requested time is not available and suggest available schedules if any.",
  "schedule_id": null
}}

If user wants to book an appointment:
Return:
{{
  "intent": "appointment",
  "patient_name": "...",
  "phone": "...",
  "complaint": "...",
  "preferred_time": "...",
  "doctor_name": "...",
  "service_name": "...",
  "schedule_id": 1
}}

If user is an existing patient, use patient context to understand previous visits, but do not invent new facts.

Missing values must be null.

Rules:
- Return JSON only.
- Do not give medical diagnosis.
- Do not invent prices, doctors, addresses, schedules, or patient history.
- If information is missing, say administrator will clarify.
- Always answer in Armenian.

User message:
{user_message}
"""

    content = call_local_llm(prompt)
    data = json.loads(content)

    intent = data.get("intent")

    if intent in [
        "faq",
        "price_query",
        "service_query",
        "doctor_query",
        "working_hours_query",
    ]:
        return {
            "type": "faq",
            "answer": data.get("answer"),
        }

    if intent == "schedule_query":
        return {
            "type": "schedule_query",
            "answer": data.get("answer"),
            "schedule_id": data.get("schedule_id"),
        }

    if intent in ["cancel_appointment", "reschedule_appointment"]:
        return {
            "type": "faq",
            "answer": "Այդ փոփոխությունը կատարելու համար կլինիկայի ադմինիստրատորը կկապվի Ձեզ հետ։",
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