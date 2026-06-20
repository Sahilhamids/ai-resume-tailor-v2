from google import genai
from extractor import extract_text_from_pdf
import json
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

def generate_tailored_resume(resume_text, job_description):
    """
    Sends resume text and job description to Gemini to generate 
    a structured JSON resume tailored for ATS optimization.
    """
    
    prompt = f"""
    You are an elite ATS Resume Optimization Expert and Senior Technical Recruiter.
    Your goal is to optimize the candidate's resume for the provided Job Description while maintaining factual accuracy.

    ===========================
    RULES
    - NEVER invent jobs, degrees, projects, certifications, dates, or companies.
    - Preserve all factual information.
    - Tailor: Professional Summary, Skills (Categorized), and Project Bullet Points.
    - Use strong action verbs (Engineered, Developed, Optimized, etc.).
    - Extract: Name, Phone, Email, LinkedIn, GitHub, Portfolio.
    - If info is missing, use "Not Provided".
    - Categorize Skills strictly into: languages, backend, database, frontend, core_cs, tools.
    - Project bullets must be tailored to the JD, concise, and impact-oriented.
    
    ===========================
    OUTPUT FORMAT (Strictly Valid JSON)
    {{
        "name": "...",
        "phone": "...",
        "email": "...",
        "linkedin": "...",
        "github": "...",
        "portfolio": "...",
        "summary": "...",
        "skills": {{
            "languages": "...",
            "backend": "...",
            "database": "...",
            "frontend": "...",
            "core_cs": "...",
            "tools": "..."
        }},
        "projects": [
            {{
                "name": "...",
                "tech": "...",
                "bullets": ["...", "..."]
            }}
        ],
        "experience": [
            {{
                "title": "...",
                "company": "...",
                "dates": "...",
                "bullets": ["...", "..."]
            }}
        ],
        "degree": "...",
        "school": "...",
        "year": "...",
        "achievements": ["...", "..."],
        "certifications": ["...", "..."],
        "languages": "English, Hindi, Marathi, Urdu",
        "interview_guidance": {{
            "missing_skills": ["...", "..."],
            "study_guide": "..."
        }}
    }}
    ===========================
    RESUME DATA
    {resume_text}

    ===========================
    JOB DESCRIPTION
    {job_description}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        response_text = response.text.strip()

        # Clean JSON markdown formatting
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        return json.loads(response_text.strip())

    except Exception as e:
        print(f"AI Error: {e}")
        return None

# Local testing block
if __name__ == "__main__":
    print("1. Extracting resume text...")
    # Ensure a dummy_resume.pdf exists in the project root for local testing
    resume_text = extract_text_from_pdf("dummy_resume.pdf")

    job_description = "Looking for a Software Engineer with Python, FastAPI, and PostgreSQL experience."

    print("2. Sending to Gemini...")
    result = generate_tailored_resume(resume_text, job_description)

    if result:
        print("\n--- AI RESPONSE ---\n")
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print("AI generation failed.")