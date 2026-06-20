from google import genai
from extractor import extract_text_from_pdf
import json # <-- NEW: We need this to parse the AI's structured response
import os #for importing key
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY") # 1. Set up your API key

client = genai.Client(api_key=API_KEY)

def generate_tailored_resume(resume_text, job_description):
    # 2. Create the strict JSON prompt
    prompt = f"""
    You are an expert resume writer. 
    Compare the following Resume to the Job Description. 
    Rewrite the resume to highlight matching skills. Do not invent experience.
    
    You MUST output your response strictly as a valid JSON object matching this exact structure:
    {{
        "name": "Candidate Name",
        "email": "email@example.com",
        "phone": "123-456-7890",
        "linkedin": "linkedin.com/in/profile",
        "summary": "A brief professional summary highlighting matched skills.",
        "skills": "Skill 1, Skill 2, Skill 3",
        "experience": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "dates": "Start Date - End Date",
                "bullets": [
                    "Tailored bullet point 1",
                    "Tailored bullet point 2"
                ]
            }}
        ],
        "education": [
            {{
                "degree": "Degree Name",
                "school": "School Name",
                "year": "Graduation Year"
            }}
        ],
        "interview_guidance": "List 3 critical missing skills and a 2-sentence guide on how to prepare."
    }}

    RESUME TEXT: 
    {resume_text}
    
    JOB DESCRIPTION: 
    {job_description}
    
    Return ONLY the raw JSON format, without any formatting blocks like ```json or ```.
    
    """
    
    try:
        # 3. Send the prompt to Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # 4. Clean up the response just in case the AI adds formatting tags
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        # 5. Convert the text into a real Python dictionary using the json library
        return json.loads(response_text)
        
    except Exception as e:
        print(f"An error occurred with the AI: {e}")
        return None

# Test the function
if __name__ == "__main__":
    print("1. Extracting resume text...")
    my_resume_text = extract_text_from_pdf("dummy_resume.pdf")
    
    dummy_jd = "We are looking for a Software Engineer with strong Python skills, experience in building APIs, and a solid understanding of SQL databases."
    
    print("2. Sending data to Gemini AI. This might take a few seconds...\n")
    ai_response_dict = generate_tailored_resume(my_resume_text, dummy_jd)
    
    print("--- AI JSON RESPONSE ---")
    # This prints the dictionary out beautifully formatted!
    print(json.dumps(ai_response_dict, indent=4))
