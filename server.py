import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from extractor import extract_text
from fetch_jobs import fetch_jobs
from matcher import score_job
from scorer import get_resume_score

app = FastAPI(title="Resume Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.docx', '.txt', '.md')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    ext = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        resume_text = extract_text(tmp_path)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")
    
    os.remove(tmp_path)
    return {"resume_text": resume_text}

class ScoreResumeRequest(BaseModel):
    resume_text: str

@app.post("/api/resume/score")
async def score_resume_endpoint(req: ScoreResumeRequest):
    try:
        result = get_resume_score(req.resume_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class JobSearchRequest(BaseModel):
    what: str
    where: str = ""
    pages: int = 1
    source: str = "both"
    experience: str = ""

@app.post("/api/jobs/search")
async def search_jobs(req: JobSearchRequest):
    try:
        jobs = fetch_jobs(what=req.what, where=req.where, pages=req.pages, source=req.source, experience=req.experience)
        formatted_jobs = []
        for job in jobs:
            title = job.get("title", "Untitled")
            company = job.get("company", "Unknown")
            location = job.get("location", "")
            desc = job.get("description", "")
            apply_url = job.get("redirect_url", "")
            source = job.get("source", "Unknown")
            
            jd_text = f"Title: {title}\nCompany: {company}\nLocation: {location}\nSource: {source}\nApply link: {apply_url}\n\n{desc}"
            
            formatted_jobs.append({
                "job_name": f"[{source}] {title} - {company}",
                "jd_text": jd_text,
                "apply_url": apply_url,
                "title": title,
                "company": company,
                "location": location,
                "source": source
            })
        return {"jobs": formatted_jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class JobData(BaseModel):
    job_name: str
    jd_text: str
    apply_url: str
    title: str
    company: str
    location: str
    source: str = "Unknown"

class CompareRequest(BaseModel):
    resume_text: str
    jobs: List[JobData]

@app.post("/api/jobs/compare")
async def compare_jobs(req: CompareRequest):
    results = []
    for job in req.jobs:
        score_res = score_job(req.resume_text, job.jd_text)
        results.append({
            "job_name": job.job_name,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "match_score": score_res["combined_score"],
            "skill_overlap_pct": score_res["skill_overlap_pct"],
            "semantic_similarity_pct": score_res["semantic_similarity_pct"],
            "matched_skills": score_res["matched_skills"],
            "missing_skills": score_res["missing_skills"],
            "apply_url": job.apply_url,
            "source": job.source
        })
    
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return {"results": results}

ui_dist_path = os.path.join(os.path.dirname(__file__), "ui", "dist")
if os.path.exists(ui_dist_path):
    app.mount("/", StaticFiles(directory=ui_dist_path, html=True), name="ui")
else:
    @app.get("/")
    def read_root():
        return {"message": "UI build not found. Please build the UI first."}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
