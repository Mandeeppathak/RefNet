# backend/api/routes.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import shutil, os, json
from uuid import uuid4

from backend.core.parser import parse_resume, parse_job_description
from backend.core.embedder import embed_and_store_resume, embed_and_store_jd, find_matching_jds_for_candidate
from backend.core.gap_analyzer import analyze_gaps, generate_referral_message
from backend.core.database import get_db, User, CandidateProfile, ReferrerProfile, JobDescription, MatchRequest
from backend.core.auth import get_current_user
from backend.api.auth_routes import router as auth_router

app = FastAPI(title="RefNet API", version="1.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register auth routes
app.include_router(auth_router)


class JDRequest(BaseModel):
    jd_id: str
    jd_text: str

class AnalyzeRequest(BaseModel):
    candidate_id: str
    jd_id: str


@app.get("/")
def root():
    return {"message": "RefNet API is running"}


@app.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # protected route
):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can upload resumes")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    temp_path = f"data/resumes/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    parsed = parse_resume(temp_path)
    os.remove(temp_path)

    # save to database
    existing = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if existing:
        existing.skills = ", ".join(parsed.get("skills", []))
        existing.experience_years = parsed.get("total_years_experience", 0)
        existing.summary = parsed.get("summary", "")
        existing.resume_parsed_json = json.dumps(parsed)
        profile = existing
    else:
        profile = CandidateProfile(
            id=str(uuid4()),
            user_id=current_user.id,
            skills=", ".join(parsed.get("skills", [])),
            experience_years=parsed.get("total_years_experience", 0),
            summary=parsed.get("summary", ""),
            resume_parsed_json=json.dumps(parsed)
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    # embed into chromadb
    embed_and_store_resume(profile.id, parsed)

    return {"profile_id": profile.id, "parsed_profile": parsed}


@app.post("/jd")
def submit_jd(
    request: JDRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "referrer":
        raise HTTPException(status_code=403, detail="Only referrers can post JDs")

    parsed = parse_job_description(request.jd_text)

    existing = db.query(JobDescription).filter(JobDescription.id == request.jd_id).first()
    if existing:
        existing.parsed_json = json.dumps(parsed)
        existing.jd_text = request.jd_text
    else:
        jd = JobDescription(
            id=request.jd_id,
            company=parsed.get("company", ""),
            job_title=parsed.get("job_title", ""),
            jd_text=request.jd_text,
            parsed_json=json.dumps(parsed)
        )
        db.add(jd)

    db.commit()
    embed_and_store_jd(request.jd_id, parsed)

    return {"jd_id": request.jd_id, "parsed_jd": parsed}


@app.get("/match/{profile_id}")
def match_candidate(
    profile_id: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user)
):
    matches = find_matching_jds_for_candidate(profile_id, top_k)
    if not matches:
        raise HTTPException(status_code=404, detail="No matches found")
    return {"profile_id": profile_id, "matches": matches}


@app.post("/analyze")
def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # fetch from database — no more memory loss on restart
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == request.candidate_id
    ).first()
    jd = db.query(JobDescription).filter(
        JobDescription.id == request.jd_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")

    parsed_resume = json.loads(profile.resume_parsed_json)
    parsed_jd = json.loads(jd.parsed_json)

    gap = analyze_gaps(parsed_resume, parsed_jd)
    message = generate_referral_message(parsed_resume, parsed_jd, gap)

    # save match request to db
    match = MatchRequest(
        id=str(uuid4()),
        candidate_id=profile.id,
        referrer_id=request.candidate_id,  # placeholder until referrer system
        jd_id=jd.id,
        match_score=gap.get("match_percentage", 0),
        gap_analysis_json=json.dumps(gap),
        referral_message=message
    )
    db.add(match)
    db.commit()

    return {
        "candidate_id": request.candidate_id,
        "jd_id": request.jd_id,
        "gap_analysis": gap,
        "referral_message": message
    }
@app.get("/referral/accept/{match_request_id}")
def accept_referral(match_request_id: str, db: Session = Depends(get_db)):
    """
    WHY: Referrer clicks Accept in email → this route fires.
    Reveals candidate identity and notifies them.
    """
    from backend.automation.notifier import notify_referral_accepted

    match = db.query(MatchRequest).filter(MatchRequest.id == match_request_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match request not found")

    if match.status != "pending":
        return {"message": f"Already {match.status}"}

    match.status = "accepted"
    db.commit()

    # get candidate details to reveal to referrer
    candidate_profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == match.candidate_id
    ).first()
    candidate_user = db.query(User).filter(User.id == candidate_profile.user_id).first()
    jd = db.query(JobDescription).filter(JobDescription.id == match.jd_id).first()
    referrer = db.query(ReferrerProfile).filter(ReferrerProfile.id == match.referrer_id).first()
    referrer_user = db.query(User).filter(User.id == referrer.user_id).first()

    # update referrer stats
    referrer.referral_count += 1
    referrer.reputation_score = round(referrer.reputation_score + 1.0, 1)
    db.commit()

    # notify candidate
    notify_referral_accepted(
        candidate_email=candidate_user.email,
        candidate_name=candidate_user.full_name,
        job_title=jd.job_title,
        company=jd.company,
        referrer_name=referrer_user.full_name
    )

    return {
        "message": "Referral accepted",
        "candidate_name": candidate_user.full_name,
        "candidate_email": candidate_user.email,
        "candidate_skills": candidate_profile.skills,
        "referral_message": match.referral_message
    }


@app.get("/referral/decline/{match_request_id}")
def decline_referral(match_request_id: str, db: Session = Depends(get_db)):
    match = db.query(MatchRequest).filter(MatchRequest.id == match_request_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match request not found")

    match.status = "rejected"
    db.commit()

    return {"message": "Referral declined"}


    from backend.core.skill_verifier import generate_assessment, grade_assessment
from backend.core.database import CandidateProfile
import json

class GradeRequest(BaseModel):
    skill: str
    answers: list

@app.get("/verify/assessment/{skill}")
def get_assessment(
    skill: str,
    level: str = "intermediate",
    current_user: User = Depends(get_current_user)
):
    """Generate a skill assessment for the candidate."""
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can take assessments")
    assessment = generate_assessment(skill, level)
    # strip correct answers before sending to frontend
    for q in assessment.get("questions", []):
        q.pop("correct", None)
        q.pop("explanation", None)
    return assessment


@app.post("/verify/grade")
def grade_skill(
    request: GradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Grade submitted answers and update candidate profile if passed."""
    result = grade_assessment(request.skill, request.answers)

    if result.get("verified"):
        # add verified badge to candidate profile
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.id
        ).first()
        if profile:
            verified = json.loads(profile.verified_skills or "[]")
            if request.skill not in verified:
                verified.append(request.skill)
            profile.verified_skills = json.dumps(verified)
            db.commit()

    return result


from backend.core.company_cards import generate_company_card

@app.get("/company/{company_name}")
def get_company_card(
    company_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    WHY: Before applying or asking for a referral,
    candidates should know exactly what they're getting into.
    """
    card = generate_company_card(company_name)
    return card
