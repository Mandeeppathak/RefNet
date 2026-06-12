from backend.core.parser import parse_job_description
from backend.core.embedder import embed_and_store_jd, embed_and_store_resume, find_matching_jds_for_candidate
from backend.core.gap_analyzer import analyze_gaps, generate_referral_message
import json

jd_text = """
Software Engineer - Backend, Razorpay Bangalore
2+ years required. Must have: Python, REST APIs, PostgreSQL, AWS.
Nice to have: Kafka, Docker, Kubernetes.
Build payment infrastructure, write scalable code, own services end to end.
"""

fake_resume = {
    "name": "Rahul Sharma",
    "email": "rahul@email.com",
    "skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Docker"],
    "experience": [{"role": "Backend Developer", "company": "Infosys",
                    "duration": "2 years", "description": "Built REST APIs and managed databases"}],
    "education": [{"degree": "B.Tech CS", "institution": "VIT", "year": "2022"}],
    "total_years_experience": 2,
    "summary": "Backend developer with Python and API experience."
}

parsed_jd = parse_job_description(jd_text)
embed_and_store_jd("razorpay_backend", parsed_jd)
embed_and_store_resume("rahul@email.com", fake_resume)

matches = find_matching_jds_for_candidate("rahul@email.com")
print("\n🎯 Match Results:")
print(json.dumps(matches, indent=2))

gap = analyze_gaps(fake_resume, parsed_jd)
print("\n🔍 Gap Analysis:")
print(json.dumps(gap, indent=2))

message = generate_referral_message(fake_resume, parsed_jd, gap)
print("\n✉️ Referral Message:")
print(message)
