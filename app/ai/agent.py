import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.ai.prompts import EXTRACTION_PROMPT

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)


def process_message(text: str):
    prompt = f"""
{EXTRACTION_PROMPT}

User message:

{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You extract structured JSON from Armenian dental clinic messages. Return JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)

        missing = []

        if not data.get("patient_name"):
            missing.append("name")

        if not data.get("phone"):
            missing.append("phone")

        if not data.get("preferred_time"):
            missing.append("time")

        return {
            "ready": len(missing) == 0,
            "missing": missing,
            "data": data,
        }

    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "raw_response": content,
        }