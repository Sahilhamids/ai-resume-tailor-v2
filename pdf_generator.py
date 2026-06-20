from jinja2 import Environment, FileSystemLoader
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa
import os

def create_pdf_from_json(json_data, output_filename="tailored_resume.pdf"):
    # 1. Load the HTML template using Jinja2
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('resume.html')
    
    # 2. Safely map the JSON data into the HTML variables
    html_content = template.render(
        name=json_data.get("name", "Name Not Found"),
        email=json_data.get("email", ""),
        phone=json_data.get("phone", ""),
        linkedin=json_data.get("linkedin", ""),
        summary=json_data.get("summary", ""),
        skills=json_data.get("skills", ""),
        experience=json_data.get("experience", []),
        education=json_data.get("education", [])
    )
    
    # 3. Convert the populated HTML string into a physical PDF file
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
    # 4. Check for errors
    if pisa_status.err:
        print("Error creating PDF")
        return None
        
    return output_filename

# Test the function
if __name__ == "__main__":
    # A fake JSON dictionary simulating our AI's output
    dummy_ai_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-0199",
        "linkedin": "linkedin.com/in/janedoe",
        "summary": "Experienced Software Engineer with a focus on Python and APIs.",
        "skills": "Python, FastAPI, SQL, Git",
        "experience": [
            {
                "title": "Backend Developer",
                "company": "Tech Corp",
                "dates": "2023 - Present",
                "bullets": [
                    "Built RESTful APIs using FastAPI.", 
                    "Optimized SQL queries for faster database performance."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.S. Computer Science",
                "school": "State University",
                "year": "2022"
            }
        ]
    }
    
    print("Generating PDF...")
    result = create_pdf_from_json(dummy_ai_data)
    
    if result:
        print(f"Success! Check your folder for: {result}")