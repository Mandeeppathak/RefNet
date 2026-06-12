# test_email.py
from backend.automation.notifier import notify_candidate_matched

fake_gap = {
    "strong_points": ["Python", "REST APIs", "PostgreSQL"],
    "missing_critical": ["AWS"],
    "action_plan": [
        {"action": "Learn AWS basics", "timeline": "1 month", "resource": "AWS Free Tier"}
    ],
    "referral_readiness": "Ready after AWS certification"
}

notify_candidate_matched(
    candidate_email="themandeeppathak@gmail.com",  # ← put your real email here
    candidate_name="Rahul Sharma",
    job_title="Backend Engineer",
    company="Razorpay",
    match_score=78.5,
    gap_analysis=fake_gap
)
