import os
import json
from google import genai
from dotenv import load_dotenv
from extractor import extract_text_from_pdf

# Load API Key securely
load_dotenv()
API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

def generate_tailored_resume(resume_text, job_description):
    """
    Sends resume text and job description to Gemini to generate 
    a structured JSON resume tailored for ATS optimization.
    """
    
    prompt = f"""
    You are an elite ATS Resume Optimization Expert.
    Optimize the candidate's resume for the Job Description. 
    Output strictly valid JSON matching this schema:
    {{
        "name": "...", "phone": "...", "email": "...", "linkedin": "...", "github": "...", "portfolio": "...",
        "summary": "...",
        "skills": {{"languages": "...", "backend": "...", "database": "...", "frontend": "...", "core_cs": "...", "tools": "..."}},
        "projects": [{{"name": "...", "tech": "...", "bullets": ["..."]}}],
        "experience": [{{"title": "...", "company": "...", "dates": "...", "bullets": ["..."]}}],
        "degree": "...", "school": "...", "year": "...",
        "achievements": ["..."], "certifications": ["..."], "languages": "English, Hindi, Marathi, Urdu",
        "interview_guidance": {{"missing_skills": ["..."], "study_guide": "..."}}
    }}
    RESUME DATA: {resume_text}
    JOB DESCRIPTION: {job_description}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        # Clean JSON markdown formatting if present
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        return None