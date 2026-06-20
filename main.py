from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
import sqlite3 # <-- NEW: Importing the database library

# Importing the functions you already built!
from extractor import extract_text_from_pdf
from ai_agent import generate_tailored_resume

app = FastAPI(title="AI Resume Tailor API")

@app.post("/tailor-resume")
async def tailor_resume(
    job_description: str = Form(...), 
    resume_file: UploadFile = File(...)
):
    # 1. Save the uploaded resume temporarily so our extractor can read it
    temp_file_path = f"temp_{resume_file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)
    
    try:
        # 2. Extract the text using your existing function
        resume_text = extract_text_from_pdf(temp_file_path)
        
        # 3. Send to Gemini AI using your existing function
        ai_response = generate_tailored_resume(resume_text, job_description)
        
        # --- NEW DATABASE LOGIC ---
        # 4. Connect to the database and log the data
        try:
            conn = sqlite3.connect('resume_app.db')
            cursor = conn.cursor()
            
            # Using placeholders (?) prevents SQL injection attacks!
            cursor.execute('''
                INSERT INTO generated_resumes (job_description, filename, ai_analysis)
                VALUES (?, ?, ?)
            ''', (job_description, resume_file.filename, ai_response))
            
            conn.commit()
            conn.close()
        except Exception as db_error:
            print(f"Database error: {db_error}")
        # --------------------------
        
        # 5. Return the AI's analysis
        return {
            "status": "success",
            "filename": resume_file.filename,
            "ai_analysis": ai_response
        }
        
    finally:
        # 6. Clean up by deleting the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)