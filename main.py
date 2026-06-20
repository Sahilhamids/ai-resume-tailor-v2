from fastapi import FastAPI, UploadFile, File, Form
from extractor import extract_text_from_pdf
from ai_agent import analyze_resume

app = FastAPI()

@app.post("/audit-resume")
async def audit_resume(job_description: str = Form(...), resume_file: UploadFile = File(...), role: str = Form(...)):
    resume_text = extract_text_from_pdf(await resume_file.read())
    analysis = analyze_resume(resume_text, job_description, role)
    return {"analysis": analysis}