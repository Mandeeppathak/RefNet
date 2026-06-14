from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    referrer_profile = relationship("ReferrerProfile", back_populates="user", uselist=False)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    skills = Column(Text)
    experience_years = Column(Float)
    summary = Column(Text)
    resume_parsed_json = Column(Text)
    verified_skills = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="candidate_profile")
    match_requests = relationship("MatchRequest", back_populates="candidate")


class ReferrerProfile(Base):
    __tablename__ = "referrer_profiles"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)
    job_title = Column(String)
    can_refer_for_roles = Column(Text)
    referral_count = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="referrer_profile")
    match_requests = relationship("MatchRequest", back_populates="referrer")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(String, primary_key=True)
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    jd_text = Column(Text, nullable=False)
    parsed_json = Column(Text)
    is_active = Column(Boolean, default=True)
    posted_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    match_requests = relationship("MatchRequest", back_populates="job")


class MatchRequest(Base):
    __tablename__ = "match_requests"
    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidate_profiles.id"), nullable=False)
    referrer_id = Column(String, ForeignKey("referrer_profiles.id"), nullable=True)
    jd_id = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    match_score = Column(Float)
    gap_analysis_json = Column(Text)
    referral_message = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    candidate = relationship("CandidateProfile", back_populates="match_requests")
    referrer = relationship("ReferrerProfile", back_populates="match_requests")
    job = relationship("JobDescription", back_populates="match_requests")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
