# backend/core/gap_analyzer.py
import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_gaps(parsed_resume: dict, parsed_jd: dict) -> dict:
    prompt = f"""
You are a senior hiring manager. Analyze this candidate vs job requirement.

CANDIDATE:
- Skills: {", ".join(parsed_resume.get("skills", []))}
- Years experience: {parsed_resume.get("total_years_experience", 0)}
- Summary: {parsed_resume.get("summary", "")}

JOB: {parsed_jd.get("job_title")} at {parsed_jd.get("company")}
- Required: {", ".join(parsed_jd.get("required_skills", []))}
- Preferred: {", ".join(parsed_jd.get("preferred_skills", []))}
- Min experience: {parsed_jd.get("min_experience_years", 0)} years

Return ONLY a JSON object with:
- overall_verdict: "Strong Match" | "Good Match" | "Partial Match" | "Weak Match"
- match_percentage: number 0-100
- strong_points: list of strings
- missing_critical: list of strings (dealbreakers)
- missing_preferred: list of strings
- experience_gap: string
- action_plan: list of objects with keys: action, priority, timeline, resource
- referral_readiness: string
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(raw.replace("```json", "").replace("```", "").strip())


def generate_referral_message(parsed_resume: dict, parsed_jd: dict, gap_analysis: dict) -> str:
    prompt = f"""
Write a referral request message for {parsed_resume.get("name")} applying for
{parsed_jd.get("job_title")} at {parsed_jd.get("company")}.

Their strengths: {", ".join(gap_analysis.get("strong_points", []))}

Rules: max 4 sentences, confident, mention 2-3 specific matching skills,
clear ask at end, no mention of gaps, sound human not templated.
Return ONLY the message text.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()
