# backend/automation/scraper.py
import requests
from bs4 import BeautifulSoup
import time, json, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.core.parser import parse_job_description
from backend.core.embedder import embed_and_store_jd
from backend.core.database import SessionLocal, JobDescription

load_dotenv()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")


def scrape_adzuna(role: str, country: str = "in", pages: int = 2) -> list[dict]:
    """
    WHY: Adzuna aggregates jobs from LinkedIn, Indeed, Naukri, Glassdoor
    and 50+ boards into one clean API. Completely legal, structured data.
    country='in' targets India specifically.
    """
    jobs = []
    for page in range(1, pages + 1):
        try:
            url = (
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
                f"?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_API_KEY}"
                f"&results_per_page=10&what={role.replace(' ', '%20')}"
                f"&content-type=application/json"
            )
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            for job in data.get("results", []):
                description = job.get("description", "")
                jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", "Unknown"),
                    "location": job.get("location", {}).get("display_name", ""),
                    "description": description[:1500],
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "source": "adzuna",
                    "url": job.get("redirect_url", "")
                })

            time.sleep(0.3)  # respect rate limits

        except Exception as e:
            print(f"⚠️ Adzuna page {page} failed for '{role}': {e}")
            continue

    return jobs


def scrape_remoteok(role: str = "python") -> list[dict]:
    """Free JSON API for remote jobs globally."""
    jobs = []
    try:
        response = requests.get(
            f"https://remoteok.com/api?tag={role}",
            headers={**HEADERS, "Accept": "application/json"},
            timeout=10
        )
        data = response.json()
        for job in data[1:11]:
            jobs.append({
                "title": job.get("position", ""),
                "company": job.get("company", ""),
                "location": "Remote",
                "description": job.get("description", "")[:1500],
                "salary_min": None,
                "salary_max": None,
                "source": "remoteok",
                "url": job.get("url", "")
            })
    except Exception as e:
        print(f"⚠️ RemoteOK failed for '{role}': {e}")
    return jobs


def scrape_naukri(role: str, location: str = "bangalore") -> list[dict]:
    """Fallback scraper for Naukri India."""
    jobs = []
    try:
        url = f"https://www.naukri.com/{role.replace(' ', '-')}-jobs-in-{location}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("article", class_="jobTuple")
        for card in cards[:10]:
            try:
                title = card.find("a", class_="title")
                company = card.find("a", class_="subTitle")
                desc = card.find("ul", class_="tags-gt")
                if title and company:
                    jobs.append({
                        "title": title.text.strip(),
                        "company": company.text.strip(),
                        "location": location,
                        "description": desc.text.strip() if desc else "",
                        "salary_min": None,
                        "salary_max": None,
                        "source": "naukri",
                        "url": title.get("href", "")
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ Naukri failed for '{role}': {e}")
    return jobs


def process_and_store_jobs(jobs: list[dict]):
    db: Session = SessionLocal()
    stored = skipped = 0

    for job in jobs:
        try:
            jd_text = f"""
{job['title']} at {job['company']}
Location: {job.get('location', 'Not specified')}
{f"Salary: ₹{job['salary_min']} - ₹{job['salary_max']}" if job.get('salary_min') else ""}
{job['description']}
            """.strip()

            if len(jd_text) < 50:
                skipped += 1
                continue

            # stable dedup ID
            raw_id = f"{job['company']}_{job['title']}"
            jd_id = "".join(c for c in raw_id.lower().replace(" ", "_") if c.isalnum() or c == "_")[:80]

            if db.query(JobDescription).filter(JobDescription.id == jd_id).first():
                skipped += 1
                continue

            parsed = parse_job_description(jd_text)

            jd_record = JobDescription(
                id=jd_id,
                company=job['company'],
                job_title=job['title'],
                jd_text=jd_text,
                parsed_json=json.dumps(parsed)
            )
            db.add(jd_record)
            db.commit()

            embed_and_store_jd(jd_id, parsed)
            stored += 1
            print(f"✅ Stored: {job['title']} at {job['company']} [{job['source']}]")
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Failed: {job.get('title', '?')}: {e}")
            db.rollback()
            continue

    db.close()
    print(f"\n📊 Done — stored: {stored}, skipped: {skipped}")


def run_scraper():
    print("🔍 Starting job scraper...")
    all_jobs = []

    # Adzuna — India jobs (aggregates LinkedIn, Indeed, Naukri, Glassdoor)
    print("📡 Fetching from Adzuna (India)...")
    for role in ["software engineer", "backend developer", "data scientist", "python developer"]:
        all_jobs += scrape_adzuna(role, country="in", pages=1)

    # Adzuna — UK/US remote roles
    print("📡 Fetching remote roles...")
    for role in ["python developer", "backend engineer"]:
        all_jobs += scrape_adzuna(role, country="gb", pages=1)

    # RemoteOK
    print("📡 Fetching from RemoteOK...")
    for role in ["python", "backend", "react", "devops"]:
        all_jobs += scrape_remoteok(role)

    # Naukri fallback
    print("📡 Fetching from Naukri...")
    all_jobs += scrape_naukri("software engineer", "bangalore")
    all_jobs += scrape_naukri("backend developer", "pune")

    print(f"📥 Total scraped: {len(all_jobs)} jobs")
    process_and_store_jobs(all_jobs)
