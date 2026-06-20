from fastapi import FastAPI, UploadFile, File, Form
from extractor import extract_text_from_pdf
from ai_agent import generate_tailored_resume
import sqlite3

app = FastAPI()

@app.post("/tailor-resume")
async def tailor_resume(job_description: str = Form(...), resume_file: UploadFile = File(...)):
    file_bytes = await resume_file.read()
    resume_text = extract_text_from_pdf(file_bytes)
    ai_data = generate_tailored_resume(resume_text, job_description)
    
    # Simple SQLite Logging
    conn = sqlite3.connect('resume_app.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS Generated_Resumes (job_desc TEXT, filename TEXT)')
    cursor.execute('INSERT INTO Generated_Resumes (job_desc, filename) VALUES (?, ?)', (job_description, resume_file.filename))
    conn.commit()
    conn.close()
    
    return {"ai_analysis": ai_data}