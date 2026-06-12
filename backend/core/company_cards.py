# backend/core/company_cards.py
# WHY: Candidates apply blindly to companies with toxic cultures,
# layoff histories, or fake job postings. This gives them real intel
# before they waste time applying — scraped from public sources.

import os, json, requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")


def fetch_company_job_data(company: str) -> dict:
    """
    WHY: Pull real hiring data for this company from Adzuna.
    Shows how actively they're hiring and what roles.
    """
    try:
        url = (
            f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            f"?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_API_KEY}"
            f"&results_per_page=5&where={company.replace(' ', '%20')}"
            f"&content-type=application/json"
        )
        response = requests.get(url, timeout=10)
        data = response.json()
        results = data.get("results", [])
        return {
            "active_listings": data.get("count", 0),
            "sample_roles": [r.get("title", "") for r in results[:5]],
            "avg_salary": _avg_salary(results),
        }
    except Exception:
        return {"active_listings": 0, "sample_roles": [], "avg_salary": None}


def _avg_salary(results: list) -> str:
    salaries = [r["salary_min"] for r in results if r.get("salary_min")]
    if not salaries:
        return "Not disclosed"
    avg = sum(salaries) / len(salaries)
    return f"₹{int(avg):,} avg minimum"


def generate_company_card(company: str) -> dict:
    """
    WHY: Synthesize everything we know about a company into
    a structured transparency card candidates can trust.
    Uses LLM knowledge + live Adzuna data combined.
    """
    job_data = fetch_company_job_data(company)

    prompt = f"""
You are a career intelligence analyst. Generate a company transparency card for: {company}

Live data we have:
- Active job listings: {job_data['active_listings']}
- Current open roles: {', '.join(job_data['sample_roles']) or 'Unknown'}
- Salary data: {job_data['avg_salary']}

Based on your knowledge about this company, return ONLY a JSON object with:
- company_name: string
- industry: string
- headquarters: string
- founded_year: number or null
- company_size: string (e.g. "1000-5000 employees")
- hiring_status: "Actively Hiring" | "Selective Hiring" | "Hiring Freeze" | "Unknown"
- active_listings: number (use the live data above)
- tech_stack: list of strings (known technologies they use)
- known_for: list of strings (2-3 things company is well known for)
- culture_signals: list of strings (positive signals from public info)
- red_flags: list of strings (any known concerns — layoffs, reviews, etc. Be honest)
- layoff_history: string (any known layoffs, or "No major layoffs reported")
- ai_disruption_risk: "Low" | "Medium" | "High" (how much AI threatens this company's jobs)
- interview_difficulty: "Easy" | "Medium" | "Hard" | "Very Hard"
- interview_process: string (typical process in 1-2 sentences)
- glassdoor_rating: number or null (approximate if known, else null)
- verdict: string (2 sentence honest summary for a job seeker)
- refnet_score: number 0-100 (overall company health score for job seekers)
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()
    try:
        card = json.loads(raw)
    except json.JSONDecodeError:
        card = json.loads(raw.replace("```json", "").replace("```", "").strip())

    # merge live data
    card["active_listings"] = job_data["active_listings"]
    card["current_roles"] = job_data["sample_roles"]
    card["salary_data"] = job_data["avg_salary"]
    return card
