import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv

# Import your custom modules
from extractor import extract_text_from_pdf
from ai_agent import generate_tailored_resume

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Resume Tailor API")

@app.post("/tailor-resume")
async def tailor_resume(
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    try:
        # 1. Read the uploaded file bytes
        file_bytes = await resume_file.read()
        
        # 2. Extract text from the PDF bytes using PyMuPDF
        resume_text = extract_text_from_pdf(file_bytes)
        
        # 3. Send to Gemini AI for analysis and JSON generation
        ai_data = generate_tailored_resume(resume_text, job_description)
        
        # 4. Log user activity to Local SQLite Database
        try:
            guidance = str(ai_data.get("interview_guidance", "No guidance")) if ai_data else "No guidance"
            
            # Connect to local SQLite database
            conn = sqlite3.connect('resume_app.db')
            cursor = conn.cursor()
            
            # Safety Check: Recreate table if Render's free tier wiped the disk
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Generated_Resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_description TEXT,
                    filename TEXT,
                    guidance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert the record
            cursor.execute('''
                INSERT INTO Generated_Resumes (job_description, filename, guidance)
                VALUES (?, ?, ?)
            ''', (job_description, resume_file.filename, guidance))
            
            conn.commit()
            conn.close()
            print("Logged to local SQLite database successfully!")
            
        except Exception as db_error:
            print(f"Database logging error: {db_error}")
            
        # 5. Return the AI data to the Streamlit frontend
        return {"ai_analysis": ai_data}

    except Exception as e:
        return {"error": str(e)}