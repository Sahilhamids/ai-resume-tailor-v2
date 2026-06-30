from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

AVAILABLE_TEMPLATES = ["modern", "classic", "minimal"]


def render_resume_html(json_data, template="modern"):
    """Renders the resume HTML for either a live preview or a PDF export."""
    if template not in AVAILABLE_TEMPLATES:
        template = "modern"

    env = Environment(loader=FileSystemLoader("templates"))
    tpl = env.get_template(f"{template}.html")

    return tpl.render(
        name=json_data.get("name", ""),
        phone=json_data.get("phone", ""),
        email=json_data.get("email", ""),
        linkedin=json_data.get("linkedin", ""),
        github=json_data.get("github", ""),
        summary=json_data.get("summary", ""),
        skills=json_data.get("skills", []),
        experience=json_data.get("experience", []),
        projects=json_data.get("projects", []),
    )


def create_pdf_from_json(json_data, output_filename="tailored_resume.pdf", template="modern"):
    html_content = render_resume_html(json_data, template)

    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    return output_filename if not pisa_status.err else None
