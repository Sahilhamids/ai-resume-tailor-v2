from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def create_pdf_from_json(json_data, output_filename="tailored_resume.pdf"):
    # Load HTML template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('resume.html')
    
    # Map all JSON data fields to the HTML template
    html_content = template.render(
        name=json_data.get("name", ""),
        phone=json_data.get("phone", ""),
        email=json_data.get("email", ""),
        linkedin=json_data.get("linkedin", ""),
        github=json_data.get("github", ""),
        portfolio=json_data.get("portfolio", ""),
        summary=json_data.get("summary", ""),
        skills=json_data.get("skills", {}),
        experience=json_data.get("experience", []),
        projects=json_data.get("projects", []),
        degree=json_data.get("degree", ""),
        school=json_data.get("school", ""),
        year=json_data.get("year", ""),
        achievements=json_data.get("achievements", []),
        certifications=json_data.get("certifications", []),
        languages=json_data.get("languages", "English, Hindi, Marathi, Urdu")
    )
    
    # Convert HTML to PDF
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
    return output_filename if not pisa_status.err else None