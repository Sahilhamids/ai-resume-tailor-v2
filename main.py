import os
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from supabase import create_client, Client

# Import your custom modules
from extractor import extract_text_from_pdf
from ai_agent import generate_tailored_resume

# Load environment variables (API_KEY, SUPABASE_URL, SUPABASE_KEY)
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

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
        
        # 4. Log user activity to Supabase Cloud Database
        try:
            # We extract the guidance safely in case the AI format breaks
            guidance = str(ai_data.get("interview_guidance", "No guidance")) if ai_data else "No guidance"
            
            # Insert the record into your Supabase table
            data, count = supabase.table('generated_resumes').insert({
                "job_description": job_description,
                "filename": resume_file.filename,
                "guidance": guidance
            }).execute()
            print("Logged to Supabase cloud successfully!")
            
        except Exception as db_error:
            print(f"Database logging error: {db_error}")
            
        # 5. Return the AI data to the Streamlit frontend
        return {"ai_analysis": ai_data}

    except Exception as e:
        return {"error": str(e)}