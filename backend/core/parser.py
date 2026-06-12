# backend/core/parser.py
# WHY: Takes messy resume PDFs and raw JD text → returns clean structured JSON

import fitz
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text.strip()


def _clean_and_parse(raw: str) -> dict:
    # single place to clean LLM output — used by both functions below
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def parse_resume(pdf_path: str) -> dict:
    """
    WHY: PDF → raw text → LLM → structured dict
    We use llama-3.1-8b-instant (fast, cheap) for resume parsing
    since it's a straightforward extraction task
    """
    raw_text = extract_text_from_pdf(pdf_path)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume parser. "
                    "Return ONLY a valid JSON object with these keys:\n"
                    "- name (string)\n"
                    "- email (string)\n"
                    "- phone (string)\n"
                    "- skills (list of strings)\n"
                    "- experience (list of objects: company, role, duration, description)\n"
                    "- education (list of objects: institution, degree, year)\n"
                    "- total_years_experience (number)\n"
                    "- summary (2 sentence candidate summary)"
                )
            },
            {
                "role": "user",
                "content": f"Parse this resume:\n\n{raw_text[:3000]}"
            }
        ],
        temperature=0
    )
    return _clean_and_parse(response.choices[0].message.content)


def parse_job_description(jd_text: str) -> dict:
    """
    WHY: Raw JD text → structured dict
    We use llama-3.3-70b-versatile (smarter) for JDs because
    JDs have subtle requirements that need deeper understanding
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert HR assistant. "
                    "Return ONLY a valid JSON object with these keys:\n"
                    "- job_title (string)\n"
                    "- company (string)\n"
                    "- required_skills (list of strings)\n"
                    "- preferred_skills (list of strings)\n"
                    "- min_experience_years (number)\n"
                    "- education_requirement (string)\n"
                    "- responsibilities (list of strings)\n"
                    "- summary (2 sentence role summary)"
                )
            },
            {
                "role": "user",
                "content": f"Parse this job description:\n\n{jd_text[:3000]}"
            }
        ],
        temperature=0
    )
    return _clean_and_parse(response.choices[0].message.content)
