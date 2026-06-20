import json
import os
import streamlit as st
from google import genai
from groq import Groq

# Access API keys
gemini_key = st.secrets.get("API_KEY") # Your existing Gemini key
groq_key = st.secrets.get("GROQ_API_KEY") 

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