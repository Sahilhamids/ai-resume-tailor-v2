import json
import os
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()

# Access API keys
gemini_key = os.getenv("API_KEY") # Your existing Gemini key
groq_key = os.getenv("GROQ_API_KEY")

# Initialize Clients
gemini_client = genai.Client(api_key=gemini_key)
groq_client = Groq(api_key=groq_key)

def clean_json_string(text):
    """Helper function to strip markdown from LLM outputs."""
    return text.replace("```json", "").replace("```", "").strip()

def analyze_with_gemini(prompt):
    """Attempt 1: Google Gemini"""
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return clean_json_string(response.text)

def analyze_with_groq(prompt):
    """Attempt 2: Meta Llama-3 via Groq API"""
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant", # Extremely fast, free model
        temperature=0.2,
        response_format={"type": "json_object"} # Forces valid JSON
    )
    return chat_completion.choices[0].message.content

def analyze_resume(resume_text, job_description, role_level):
    prompt = f"""
    Act as a professional Career Coach and ATS Expert.
    Analyze the following resume against the job description for a {role_level} position.
    
    Return ONLY a single valid JSON object with the following structure:
    {{
        "ats_score": 85,
        "strengths": ["Point 1", "Point 2", "Point 3"],
        "weaknesses": ["Point 1", "Point 2", "Point 3"],
        "missing_keywords": ["Keyword1", "Keyword2", "Keyword3"],
        "paraphrasing_suggestions": [
            {{"original": "Bad sentence", "suggested": "Strong version"}}
        ]
    }}
    
    RESUME: {resume_text}
    JOB DESCRIPTION: {job_description}
    """
    
    # --- THE FALLBACK CASCADE ARCHITECTURE ---
   # --- THE FALLBACK CASCADE ARCHITECTURE (DEBUG MODE) ---
    try:
        result_text = analyze_with_gemini(prompt)
        return json.loads(result_text)
        
    except Exception as gemini_error:
        try:
            result_text = analyze_with_groq(prompt)
            return json.loads(result_text)
            
        except Exception as groq_error:
            # If both fail, gracefully tell the user.
            raise Exception("All AI servers are currently busy. Please try again in 1 minute.")
            raise Exception(f"DEBUG INFO -> Gemini failed because: [{gemini_error}] | Groq failed because: [{groq_error}]")

# --- ADD THIS TO THE BOTTOM OF ai_agent.py ---

def generate_tailored_resume(profile_data, job_description):
    """
    Pipeline 1 Engine: Takes raw profile data and a JD, and generates
    strict, tailored resume content without hallucinating.
    """
    prompt = f"""
    Act as an Expert Executive Resume Writer and ATS Specialist.
    Your task is to generate highly tailored, ATS-friendly resume sections based STRICTLY on the user's provided profile data and the target Job Description.

    STRICT ANTI-HALLUCINATION RULES:
    1. DO NOT invent or fabricate any metrics, percentages, companies, degrees, or skills that are not explicitly stated in the User Profile Data.
    2. You may rephrase, reformat, and reorganize the user's existing experience to highlight relevance to the Job Description, but you must remain factual.
    3. If the user lacks a critical skill mentioned in the JD, DO NOT add it to their resume.

    Return ONLY a valid JSON object with this exact structure:
    {{
        "professional_summary": "A 3-4 sentence powerful summary tailored to the JD.",
        "tailored_employment": [
            {{
                "company": "Company Name",
                "title": "Role Title",
                "duration": "Start - End",
                "optimized_bullets": ["Bullet 1", "Bullet 2", "Bullet 3"]
            }}
        ],
        "tailored_projects": [
            {{
                "name": "Project Name",
                "optimized_description": "A tailored 2-3 sentence description focusing on relevant tech/skills."
            }}
        ],
        "top_relevant_skills": ["Skill 1", "Skill 2", "Skill 3"]
    }}

    USER PROFILE DATA:
    {profile_data}

    TARGET JOB DESCRIPTION:
    {job_description}
    """
    
    # --- THE FALLBACK CASCADE ARCHITECTURE ---
    try:
        print("Routing generation request to Primary Model: Gemini...")
        result_text = analyze_with_gemini(prompt)
        return json.loads(result_text)
        
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}. Cascading to Groq (Llama-3.1)...")
        try:
            result_text = analyze_with_groq(prompt)
            return json.loads(result_text)
            
        except Exception as groq_error:
            raise Exception("All AI servers are currently busy. Please try again in 1 minute.")
def parse_resume_to_profile(resume_text):
    """
    Reads a raw resume and extracts the data into a structured JSON format 
    that perfectly matches our database schema.
    """
    prompt = f"""
    Act as an Expert Data Extraction AI. Extract the candidate's professional profile from the following resume text.
    Return ONLY a single valid JSON object. Do not invent any data. If a field is missing, return an empty string "" or an empty list [].

    Expected JSON Structure:
    {{
        "basic_info": {{
            "full_name": "John Doe",
            "phone": "123-456-7890",
            "linkedin_url": "linkedin.com/in/...",
            "github_url": "github.com/...",
            "target_role": "Software Engineer"
        }},
        "skills": ["Python", "React", "AWS"],
        "employment": [
            {{
                "company": "Tech Corp",
                "title": "Backend Engineer",
                "start_date": "01/2020",
                "end_date": "Present",
                "responsibilities": "Maintained servers..."
            }}
        ],
        "projects": [
            {{
                "name": "E-Commerce App",
                "description": "Built using Next.js...",
                "link": "github.com/repo"
            }}
        ]
    }}

    RESUME TEXT:
    {resume_text}
    """
    
    try:
        result_text = analyze_with_gemini(prompt)
        return json.loads(result_text)
    except Exception as e:
        print(f"Gemini failed, falling back to Groq: {e}")
        result_text = analyze_with_groq(prompt)
        return json.loads(result_text)


def generate_cover_letter(profile_data, job_description, company_name):
    """
    Generates a tailored cover letter strictly from the user's factual profile data,
    following the same anti-hallucination rules as the resume builder.
    """
    prompt = f"""
    Act as an Expert Career Coach writing a compelling, concise cover letter.
    Use STRICTLY the facts in the User Profile Data below — do not invent
    metrics, companies, or skills not present there. Address the letter to
    "{company_name}" if provided, otherwise keep it generic ("Hiring Team").

    Return ONLY a valid JSON object with this exact structure:
    {{
        "subject_line": "A short, punchy subject/title for the letter",
        "body": "The full cover letter body text, 3-4 paragraphs, ready to send."
    }}

    USER PROFILE DATA:
    {profile_data}

    TARGET JOB DESCRIPTION:
    {job_description}
    """

    try:
        result_text = analyze_with_gemini(prompt)
        return json.loads(result_text)
    except Exception as e:
        print(f"Gemini failed: {e}. Cascading to Groq (Llama-3.1)...")
        try:
            result_text = analyze_with_groq(prompt)
            return json.loads(result_text)
        except Exception:
            raise Exception("All AI servers are currently busy. Please try again in 1 minute.")