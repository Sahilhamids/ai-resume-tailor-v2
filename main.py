import secrets
import uuid

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import database
from db import init_db
from auth import create_access_token, get_current_user_id
from extractor import extract_text_from_pdf
from sanitizer import sanitize_text
from validator import validate_missing_keywords
from ai_agent import analyze_resume, generate_tailored_resume, parse_resume_to_profile
from pdf_generator import create_pdf_from_json

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Career Intelligence Platform")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/assets", StaticFiles(directory="static_dist/assets"), name="assets")


@app.on_event("startup")
def on_startup():
    init_db()


# --- Schemas ---

class SignupRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    target_role: str = ""


class SkillRequest(BaseModel):
    skill_name: str


class EmploymentRequest(BaseModel):
    company: str
    role: str
    start_date: str = ""
    end_date: str = ""
    responsibilities: str = ""


class ProjectRequest(BaseModel):
    name: str
    description: str = ""
    link: str = ""


class CustomSectionRequest(BaseModel):
    title: str
    content: str


class BuildResumeRequest(BaseModel):
    job_description: str


# --- Frontend ---

@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse("static_dist/index.html")


# --- Auth ---

@app.post("/auth/anonymous")
@limiter.limit("10/minute")
def create_anonymous_session(request: Request):
    """Issues a session with no signup screen. Profile/history still persist per-browser via the JWT."""
    email = f"anon-{uuid.uuid4()}@anon.local"
    password = secrets.token_hex(16)
    database.create_user(email, password)
    user_id = database.verify_login(email, password)
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/signup")
def signup(data: SignupRequest):
    ok = database.create_user(data.email, data.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = database.verify_login(data.email, data.password)
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = database.verify_login(form_data.username, form_data.password)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}


# --- Profile ---

@app.get("/profile")
def get_profile(user_id: int = Depends(get_current_user_id)):
    profile = database.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    full_name, phone, linkedin, github, target_role = profile
    return {
        "full_name": full_name, "phone": phone, "linkedin": linkedin,
        "github": github, "target_role": target_role,
        "skills": database.get_skills(user_id),
        "employment": database.get_employment(user_id),
        "projects": database.get_projects(user_id),
        "custom_sections": database.get_custom_sections(user_id),
    }


@app.put("/profile")
def update_profile(data: ProfileUpdateRequest, user_id: int = Depends(get_current_user_id)):
    database.update_profile(user_id, data.full_name, data.phone, data.linkedin, data.github, data.target_role)
    return {"status": "ok"}


@app.post("/profile/onboard-from-pdf")
@limiter.limit("5/minute")
async def onboard_from_pdf(request: Request, resume_file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    resume_text = extract_text_from_pdf(await resume_file.read())
    parsed = parse_resume_to_profile(resume_text)

    basic_info = parsed.get("basic_info", {})
    database.update_profile(
        user_id,
        basic_info.get("full_name", ""),
        basic_info.get("phone", ""),
        basic_info.get("linkedin_url", ""),
        basic_info.get("github_url", ""),
        basic_info.get("target_role", ""),
    )
    for skill in parsed.get("skills", []):
        database.add_skill(user_id, skill)
    for job in parsed.get("employment", []):
        database.add_employment(
            user_id, job.get("company", ""), job.get("title", ""),
            job.get("start_date", ""), job.get("end_date", ""), job.get("responsibilities", ""),
        )
    for proj in parsed.get("projects", []):
        database.add_project(user_id, proj.get("name", ""), proj.get("description", ""), proj.get("link", ""))

    return {"status": "ok", "parsed": parsed}


@app.post("/profile/skills")
def add_skill(data: SkillRequest, user_id: int = Depends(get_current_user_id)):
    database.add_skill(user_id, data.skill_name)
    return {"status": "ok"}


@app.delete("/profile/skills/{skill_id}")
def delete_skill(skill_id: int, user_id: int = Depends(get_current_user_id)):
    database.delete_skill(skill_id)
    return {"status": "ok"}


@app.post("/profile/employment")
def add_employment(data: EmploymentRequest, user_id: int = Depends(get_current_user_id)):
    database.add_employment(user_id, data.company, data.role, data.start_date, data.end_date, data.responsibilities)
    return {"status": "ok"}


@app.put("/profile/employment/{job_id}")
def update_employment(job_id: int, data: EmploymentRequest, user_id: int = Depends(get_current_user_id)):
    database.update_employment_record(job_id, data.company, data.role, data.start_date, data.end_date, data.responsibilities)
    return {"status": "ok"}


@app.delete("/profile/employment/{job_id}")
def delete_employment(job_id: int, user_id: int = Depends(get_current_user_id)):
    database.delete_employment(job_id)
    return {"status": "ok"}


@app.post("/profile/projects")
def add_project(data: ProjectRequest, user_id: int = Depends(get_current_user_id)):
    database.add_project(user_id, data.name, data.description, data.link)
    return {"status": "ok"}


@app.put("/profile/projects/{project_id}")
def update_project(project_id: int, data: ProjectRequest, user_id: int = Depends(get_current_user_id)):
    database.update_project_record(project_id, data.name, data.description, data.link)
    return {"status": "ok"}


@app.delete("/profile/projects/{project_id}")
def delete_project(project_id: int, user_id: int = Depends(get_current_user_id)):
    database.delete_project(project_id)
    return {"status": "ok"}


@app.post("/profile/custom-sections")
def add_custom_section(data: CustomSectionRequest, user_id: int = Depends(get_current_user_id)):
    database.add_custom_section(user_id, data.title, data.content)
    return {"status": "ok"}


@app.put("/profile/custom-sections/{section_id}")
def update_custom_section(section_id: int, data: CustomSectionRequest, user_id: int = Depends(get_current_user_id)):
    database.update_custom_section_record(section_id, data.title, data.content)
    return {"status": "ok"}


@app.delete("/profile/custom-sections/{section_id}")
def delete_custom_section(section_id: int, user_id: int = Depends(get_current_user_id)):
    database.delete_custom_section(section_id)
    return {"status": "ok"}


# --- Pipeline 1: Build / tailor resume ---

@app.post("/resume/build")
@limiter.limit("5/minute")
def build_resume(request: Request, data: BuildResumeRequest, user_id: int = Depends(get_current_user_id)):
    profile = database.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    full_name, phone, linkedin, github, target_role = profile

    compiled_profile = {
        "target_role": target_role,
        "skills": [s for _, s in database.get_skills(user_id)],
        "employment": database.get_employment(user_id),
        "projects": database.get_projects(user_id),
    }

    try:
        result = generate_tailored_resume(compiled_profile, data.job_description)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result


@app.post("/resume/export-pdf")
def export_pdf(tailored_resume: dict, user_id: int = Depends(get_current_user_id)):
    profile = database.get_profile(user_id)
    full_name, phone, linkedin, github, target_role = profile if profile else ("", "", "", "", "")

    json_data = {
        "name": full_name,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "summary": tailored_resume.get("professional_summary", ""),
        "skills": {"Top Relevant Skills": tailored_resume.get("top_relevant_skills", [])},
        "experience": tailored_resume.get("tailored_employment", []),
        "projects": tailored_resume.get("tailored_projects", []),
    }

    output_path = f"tailored_resume_{user_id}.pdf"
    result_path = create_pdf_from_json(json_data, output_path)
    if not result_path:
        raise HTTPException(status_code=500, detail="PDF generation failed")
    return FileResponse(result_path, filename="tailored_resume.pdf", media_type="application/pdf")


# --- Pipeline 2: ATS Audit ---

@app.post("/resume/audit")
@limiter.limit("5/minute")
async def audit_resume(
    request: Request,
    job_description: str = Form(...),
    role: str = Form(...),
    resume_file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    raw_text = extract_text_from_pdf(await resume_file.read())
    sanitized_text = sanitize_text(raw_text)

    try:
        analysis = analyze_resume(sanitized_text, job_description, role)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    validation = validate_missing_keywords(raw_text, analysis.get("missing_keywords", []))
    database.save_audit(user_id, role, analysis.get("ats_score", 0))

    return {"analysis": analysis, "keyword_validation": validation}


@app.get("/resume/history")
def resume_history(user_id: int = Depends(get_current_user_id)):
    return database.get_history(user_id)


# --- SPA fallback (must stay last so it doesn't shadow API routes) ---

@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
def spa_catch_all(full_path: str):
    return FileResponse("static_dist/index.html")
