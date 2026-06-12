# backend/core/database.py
# WHY: This file does two things:
# 1. Creates the connection to PostgreSQL
# 2. Defines every table in RefNet as a Python class
# SQLAlchemy translates these classes into actual SQL tables automatically

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# engine = the actual connection to PostgreSQL
engine = create_engine(os.getenv("DATABASE_URL"))

# SessionLocal = factory that creates database sessions
# each request gets its own session, closes when done
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class all our table models inherit from
Base = declarative_base()


# ── TABLE 1: Users ───────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # uuid
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, nullable=False)  # "candidate" or "referrer"
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships — SQLAlchemy auto-joins these
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    referrer_profile = relationship("ReferrerProfile", back_populates="user", uselist=False)


# ── TABLE 2: Candidate Profiles ──────────────────────────────
class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    skills = Column(Text)           # stored as comma-separated string
    experience_years = Column(Float)
    summary = Column(Text)
    resume_parsed_json = Column(Text)  # full parsed resume as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_skills = Column(Text, default="[]")  # JSON list of verified skill names

    user = relationship("User", back_populates="candidate_profile")
    match_requests = relationship("MatchRequest", back_populates="candidate")


# ── TABLE 3: Referrer Profiles ───────────────────────────────
class ReferrerProfile(Base):
    __tablename__ = "referrer_profiles"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)
    job_title = Column(String)
    can_refer_for_roles = Column(Text)   # comma-separated roles they can refer for
    referral_count = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="referrer_profile")
    match_requests = relationship("MatchRequest", back_populates="referrer")


# ── TABLE 4: Job Descriptions ────────────────────────────────
class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True)  # e.g. "razorpay_backend_2024"
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    jd_text = Column(Text, nullable=False)
    parsed_json = Column(Text)    # parsed JD as JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    match_requests = relationship("MatchRequest", back_populates="job")


# ── TABLE 5: Match Requests ──────────────────────────────────
# WHY: This is the core of RefNet's anonymous matching system.
# A match request links a candidate to a referrer for a specific job.
# The anonymity is enforced here — status controls what's revealed.
class MatchRequest(Base):
    __tablename__ = "match_requests"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidate_profiles.id"), nullable=False)
    referrer_id = Column(String, ForeignKey("referrer_profiles.id"), nullable=False)
    jd_id = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    match_score = Column(Float)
    gap_analysis_json = Column(Text)   # stored gap analysis
    referral_message = Column(Text)    # AI generated message

    # anonymity flow:
    # pending   → referrer sees skills only, no name/photo
    # accepted  → both profiles revealed, referral proceeds
    # rejected  → candidate notified, no details shared
    # referred  → referral submitted to company
    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("CandidateProfile", back_populates="match_requests")
    referrer = relationship("ReferrerProfile", back_populates="match_requests")
    job = relationship("JobDescription", back_populates="match_requests")


# ── DB SESSION DEPENDENCY (used in FastAPI routes) ───────────
def get_db():
    # WHY: each API request gets a fresh session
    # yield gives it to the route, finally closes it after
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    # creates all tables in PostgreSQL if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
