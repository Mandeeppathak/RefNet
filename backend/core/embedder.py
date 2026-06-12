# backend/core/embedder.py
# WHY: Converts parsed text into vectors so we can mathematically
# compare resumes against JDs — this is the RAG core of RefNet

from sentence_transformers import SentenceTransformer
import chromadb

# loaded once — reloading this every call would be very slow
model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./data/vectorstore")
resume_collection = chroma_client.get_or_create_collection("resumes")
jd_collection = chroma_client.get_or_create_collection("job_descriptions")


def build_resume_text(parsed_resume: dict) -> str:
    # WHY: flatten dict → one string so the model can embed it
    skills = ", ".join(parsed_resume.get("skills", []))
    experience = " ".join([
        f"{e.get('role', '')} at {e.get('company', '')} {e.get('description', '')}"
        for e in parsed_resume.get("experience", [])
    ])
    education = " ".join([
        f"{e.get('degree', '')} from {e.get('institution', '')}"
        for e in parsed_resume.get("education", [])
    ])
    summary = parsed_resume.get("summary", "")
    return f"{summary} Skills: {skills}. Experience: {experience}. Education: {education}"


def build_jd_text(parsed_jd: dict) -> str:
    required = ", ".join(parsed_jd.get("required_skills", []))
    preferred = ", ".join(parsed_jd.get("preferred_skills", []))
    responsibilities = " ".join(parsed_jd.get("responsibilities", []))
    summary = parsed_jd.get("summary", "")
    return f"{summary} Required: {required}. Preferred: {preferred}. Responsibilities: {responsibilities}"


def embed_and_store_resume(candidate_id: str, parsed_resume: dict):
    text = build_resume_text(parsed_resume)
    vector = model.encode(text).tolist()
    resume_collection.upsert(
        ids=[candidate_id],
        embeddings=[vector],
        documents=[text],
        metadatas=[{
            "name": parsed_resume.get("name", ""),
            "email": parsed_resume.get("email", ""),
            "skills": ", ".join(parsed_resume.get("skills", [])),
            "years": str(parsed_resume.get("total_years_experience", 0))
        }]
    )
    print(f"✅ Resume embedded and stored for {candidate_id}")


def embed_and_store_jd(jd_id: str, parsed_jd: dict):
    text = build_jd_text(parsed_jd)
    vector = model.encode(text).tolist()
    jd_collection.upsert(
        ids=[jd_id],
        embeddings=[vector],
        documents=[text],
        metadatas=[{
            "job_title": parsed_jd.get("job_title", ""),
            "company": parsed_jd.get("company", ""),
            "required_skills": ", ".join(parsed_jd.get("required_skills", [])),
            "min_experience": str(parsed_jd.get("min_experience_years", 0))
        }]
    )
    print(f"✅ JD embedded and stored for {jd_id}")


def find_matching_jds_for_candidate(candidate_id: str, top_k: int = 5) -> list:
    """
    WHY: Fetch candidate's stored vector → search JD collection
    for closest vectors → return ranked matches with scores
    """
    result = resume_collection.get(ids=[candidate_id], include=["embeddings"])
    if result["embeddings"] is None or len(result["embeddings"]) == 0:
        print(f"❌ No resume found for {candidate_id}")
        return []

    candidate_vector = result["embeddings"][0]

    matches = jd_collection.query(
        query_embeddings=[candidate_vector],
        n_results=top_k,
        include=["metadatas", "distances", "documents"]
    )

    results = []
    for i in range(len(matches["ids"][0])):
        results.append({
            "jd_id": matches["ids"][0][i],
            "company": matches["metadatas"][0][i].get("company"),
            "job_title": matches["metadatas"][0][i].get("job_title"),
            # convert distance to 0-100 score: 0 distance = 100% match
            "match_score": round((1 - matches["distances"][0][i]) * 100, 1)
        })

    return sorted(results, key=lambda x: x["match_score"], reverse=True)
