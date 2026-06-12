# backend/automation/matcher.py
# WHY: This is the orchestrator — connects all pieces together.
# It runs automatically, matches candidates to referrers,
# and triggers notifications. No human intervention needed.

import json
from uuid import uuid4
from sqlalchemy.orm import Session

from backend.core.database import (
    SessionLocal, User, CandidateProfile,
    ReferrerProfile, JobDescription, MatchRequest
)
from backend.core.embedder import find_matching_jds_for_candidate
from backend.core.gap_analyzer import analyze_gaps, generate_referral_message
from backend.automation.notifier import (
    notify_candidate_matched,
    notify_referrer_new_candidate
)


def find_referrers_for_company(company: str, db: Session) -> list:
    """
    WHY: Given a company name, find all registered referrers there.
    We do case-insensitive partial match so 'Razorpay' matches 'razorpay india'
    """
    referrers = db.query(ReferrerProfile).filter(
        ReferrerProfile.company.ilike(f"%{company}%")
    ).all()
    return referrers


def match_already_exists(candidate_id: str, jd_id: str, referrer_id: str, db: Session) -> bool:
    """WHY: Prevent duplicate match requests for same candidate+jd+referrer."""
    existing = db.query(MatchRequest).filter(
        MatchRequest.candidate_id == candidate_id,
        MatchRequest.jd_id == jd_id,
        MatchRequest.referrer_id == referrer_id,
        MatchRequest.status.in_(["pending", "accepted", "referred"])
    ).first()
    return existing is not None


def process_candidate_matches(candidate_profile_id: str, db: Session):
    """
    WHY: Full pipeline for one candidate —
    find matches, analyze gaps, find referrers, send notifications.
    """
    # get candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == candidate_profile_id
    ).first()

    if not profile:
        print(f"❌ Profile not found: {candidate_profile_id}")
        return

    user = db.query(User).filter(User.id == profile.user_id).first()
    parsed_resume = json.loads(profile.resume_parsed_json)

    print(f"\n🔍 Processing matches for {user.full_name}...")

    # step 1 — find top matching JDs via vector search
    matches = find_matching_jds_for_candidate(candidate_profile_id, top_k=5)

    if not matches:
        print("⚠️ No matches found")
        return

    for match in matches:
        # only process good matches — below 20 is too weak
        if match["match_score"] < 20:
            continue

        jd_id = match["jd_id"]
        jd_record = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd_record:
            continue

        parsed_jd = json.loads(jd_record.parsed_json)

        # step 2 — gap analysis
        gap = analyze_gaps(parsed_resume, parsed_jd)
        referral_msg = generate_referral_message(parsed_resume, parsed_jd, gap)

        # step 3 — notify candidate about this match
        notify_candidate_matched(
            candidate_email=user.email,
            candidate_name=user.full_name,
            job_title=jd_record.job_title,
            company=jd_record.company,
            match_score=match["match_score"],
            gap_analysis=gap
        )

        # step 4 — find referrers at this company
        referrers = find_referrers_for_company(jd_record.company, db)

        if not referrers:
            print(f"  ℹ️ No referrers at {jd_record.company} yet")
            continue

        for referrer in referrers:
            # skip duplicate requests
            if match_already_exists(profile.id, jd_id, referrer.id, db):
                print(f"  ⏭️ Match request already exists, skipping")
                continue

            referrer_user = db.query(User).filter(User.id == referrer.user_id).first()

            # step 5 — create match request in DB
            match_request = MatchRequest(
                id=str(uuid4()),
                candidate_id=profile.id,
                referrer_id=referrer.id,
                jd_id=jd_id,
                match_score=match["match_score"],
                gap_analysis_json=json.dumps(gap),
                referral_message=referral_msg,
                status="pending"
            )
            db.add(match_request)
            db.commit()
            db.refresh(match_request)

            # step 6 — notify referrer (skills only, no identity)
            notify_referrer_new_candidate(
                referrer_email=referrer_user.email,
                referrer_name=referrer_user.full_name,
                job_title=jd_record.job_title,
                candidate_skills=profile.skills,
                match_score=match["match_score"],
                referral_message=referral_msg,
                match_request_id=match_request.id
            )

            print(f"  ✅ Match request created → referrer at {jd_record.company} notified")


def run_daily_matcher():
    """
    WHY: Runs every day automatically via APScheduler.
    Processes all active candidates and finds new matches.
    """
    print("\n⚙️ Running daily matcher...")
    db = SessionLocal()

    try:
        # get all candidates who have uploaded resumes
        profiles = db.query(CandidateProfile).filter(
            CandidateProfile.resume_parsed_json.isnot(None)
        ).all()

        print(f"👥 Processing {len(profiles)} candidates...")

        for profile in profiles:
            try:
                process_candidate_matches(profile.id, db)
            except Exception as e:
                print(f"⚠️ Failed for profile {profile.id}: {e}")
                continue

    finally:
        db.close()

    print("\n✅ Daily matching complete")
