# backend/core/skill_verifier.py
# WHY: Self-declared skills are unreliable.
# This generates role-specific assessments and grades answers.
# Verified badges = referrers trust candidates = more referrals happen.

import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_assessment(skill: str, level: str = "intermediate") -> dict:
    """
    WHY: Generate 5 MCQ questions for a specific skill.
    Questions are practical, not theoretical — we test real ability.
    """
    prompt = f"""
Generate a skill assessment for: {skill} ({level} level)

Return ONLY a JSON object with:
- skill: string
- level: string
- questions: list of 5 objects each with:
    - id: number (1-5)
    - question: string (practical scenario-based)
    - options: list of 4 strings (A, B, C, D)
    - correct: string (the correct option text)
    - explanation: string (why it's correct, 1 sentence)

Make questions practical — real scenarios a developer would face.
No trick questions. Test genuine understanding.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(raw.replace("```json", "").replace("```", "").strip())


def grade_assessment(skill: str, answers: list[dict]) -> dict:
    """
    WHY: Grade submitted answers and decide if skill is verified.
    Pass threshold: 4/5 correct (80%) — strict but fair.
    answers format: [{"question_id": 1, "selected": "option text"}, ...]
    """
    prompt = f"""
You are grading a skill assessment for: {skill}

Submitted answers:
{json.dumps(answers, indent=2)}

Grade each answer and return ONLY a JSON object with:
- skill: string
- total_questions: number
- correct_count: number
- passed: boolean (true if correct_count >= 4)
- score_percentage: number
- feedback: string (2 sentences — what they know well and what to improve)
- verified: boolean (same as passed)
- results: list of objects with: question_id, correct (boolean), explanation
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(raw.replace("```json", "").replace("```", "").strip())
