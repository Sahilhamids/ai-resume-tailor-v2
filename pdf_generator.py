from jinja2 import Environment, FileSystemLoader
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa
import os

def create_pdf_from_json(json_data, output_filename="tailored_resume.pdf"):
    # 1. Load the HTML template using Jinja2
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('resume.html')
    
    # 2. Map all JSON data fields to the HTML template
    html_content = template.render(
    name=json_data.get("name", ""),
    phone=json_data.get("phone", ""),
    email=json_data.get("email", ""),
    linkedin=json_data.get("linkedin", ""),
    github=json_data.get("github", ""),
    portfolio=json_data.get("portfolio", ""),
    summary=json_data.get("summary", ""),
    skills=json_data.get("skills", {}),  # Passes the entire dictionary to be accessed via dot notation
    experience=json_data.get("experience", []),
    projects=json_data.get("projects", []),
    degree=json_data.get("degree", ""),
    school=json_data.get("school", ""),
    year=json_data.get("year", ""),
    achievements=json_data.get("achievements", []),
    certifications=json_data.get("certifications", []),
    languages=json_data.get("languages", "English, Hindi, Marathi, Urdu")
)
    
    # 3. Convert HTML to PDF
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
    if pisa_status.err:
        print("Error creating PDF")
        return None
        
    return output_filename

# Test the function locally
if __name__ == "__main__":
    dummy_ai_data = {
        "name": "SAHIL SHAIKH",
        "phone": "+91 9146749096",
        "email": "ssahil9635@gmail.com",
        "linkedin": "linkedin.com/in/sahil-h-shaikh/",
        "github": "github.com/Sahilhamids",
        "portfolio": "sahilportfolio.com",
        "summary": "Software Developer with strong knowledge of Python, Data Structures & Algorithms.",
        "skills": {
            "languages": "Python, C++, SQL, JavaScript",
            "backend": "FastAPI, REST APIs, SQLAlchemy",
            "database": "PostgreSQL, MySQL",
            "frontend": "React, HTML, CSS",
            "core_cs": "Data Structures, Algorithms, OOP, DBMS",
            "tools": "Git, GitHub, Linux, VS Code"
        },
        "experience": [
            {
                "title": "Graduate Engineer Trainee (GET)",
                "company": "Ambuja Cements Ltd.",
                "dates": "Jul 2024 – Present",
                "bullets": ["Worked in E&I department.", "Assisted in troubleshooting industrial systems."]
            }
        ],
        "projects": [
            {
                "name": "Expense Splitter App",
                "tech": "FastAPI, PostgreSQL, React",
                "description": "Automated bill splitting among group members."
            }
        ],
        "degree": "Bachelor of Engineering (Electronics & Telecommunication)",
        "school": "Government College of Engineering, Chandrapur",
        "year": "2025",
        "achievements": ["Solved 90+ DSA problems.", "Team Leader for Major Project."],
        "certifications": ["AWS Cloud Practitioner", "Google AI Professional"],
        "languages": "English, Hindi, Marathi, Urdu"
    }
    
    print("Generating PDF...")
    result = create_pdf_from_json(dummy_ai_data)
    if result:
        print(f"Success! Check your folder for: {result}")