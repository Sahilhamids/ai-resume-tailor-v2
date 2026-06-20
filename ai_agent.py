import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))

def analyze_resume(resume_text, job_description, role_level):
    prompt = f"""
    Act as a professional Career Coach and ATS Expert.
    Analyze the resume against the job description for a {role_level} position.
    Output ONLY valid JSON.
    
    {{
        "ats_score": 75,
        "strengths": ["List 3 strong points"],
        "weaknesses": ["List 3 areas for improvement"],
        "missing_keywords": ["List 5 missing industry keywords"],
        "paraphrasing_suggestions": [
            {{"original": "Bad sentence", "suggested": "Strong, action-oriented sentence"}}
        ],
        "compliance_checklist": {{"has_images": bool, "has_columns": bool}}
    }}
    RESUME: {resume_text}
    JD: {job_description}
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)