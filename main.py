# main.py
import uvicorn
from backend.api.routes import app
from backend.core.database import create_tables
from backend.automation.scraper import run_scraper
from backend.automation.matcher import run_daily_matcher
from apscheduler.schedulers.background import BackgroundScheduler

create_tables()

scheduler = BackgroundScheduler()
scheduler.add_job(run_scraper, "interval", hours=24, id="job_scraper")
scheduler.add_job(run_daily_matcher, "interval", hours=12, id="daily_matcher")
scheduler.start()
print("⚙️ Scheduler started — scraper every 24hrs, matcher every 12hrs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
