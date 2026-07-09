import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / "secrets" / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in secrets/.env")

client = OpenAI(api_key=API_KEY)


def map_fields_with_llm(fields: list, applicant: dict) -> list:
    conversation = [
        {
            "role": "system",
            "content": """
You map job application form fields to applicant values.

Return only valid JSON array.

Allowed fields:
- first name
- last name
- email
- phone
- LinkedIn
- city
- state
- country

Do not answer:
- visa questions
- work authorization
- sponsorship
- gender
- race
- disability
- veteran status
- salary
- legal declarations
- final submit
"""
        },
        {
            "role": "user",
            "content": f"""
Applicant:
{json.dumps(applicant, indent=2)}

Visible form fields:
{json.dumps(fields, indent=2)}

Return format:
[
  {{
    "field_index": 0,
    "field_label": "First Name",
    "value": "Sai",
    "confidence": "high"
  }}
]
"""
        }
    ]

    response = client.responses.create(
        model=MODEL_NAME,
        input=conversation
    )

    raw_text = response.output_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("LLM returned non-JSON:")
        print(raw_text)
        return []