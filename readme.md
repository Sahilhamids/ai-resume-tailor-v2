AI Resume Tailor
An intelligent, ATS-optimized resume tailoring application that automatically aligns a candidate's resume with a specific job description, ensuring maximum compatibility with Applicant Tracking Systems (ATS).

🚀 Live Demo
[Link to your live Streamlit App URL]

🛠 Tech Stack
Frontend: Streamlit (Interactive UI)

Backend: FastAPI (REST API)

AI Engine: Google Gemini API (Text analysis & optimization)

PDF Engine: PyMuPDF (fitz) & xhtml2pdf

Database: SQLite (Project logging)

Deployment: Render (Backend) & Streamlit Community Cloud (Frontend)

💡 Key Features
Automated ATS Tailoring: Dynamically rewrites bullet points to match JD keywords while maintaining factual integrity.

Skill Gap Analysis: Identifies missing technical skills based on the JD to help users prepare for interviews.

One-Page Optimization: Enforces strict formatting and CSS constraints to ensure generated PDFs are ATS-friendly and perfectly sized.

Smart Extraction: Uses PyMuPDF to accurately extract text from complex, multi-column PDF layouts.

🏗 Project Architecture
Extraction Phase: The raw PDF is converted into searchable text.

Analysis Phase: Gemini AI compares the extracted text against the Job Description and generates a structured JSON response.

Tailoring Phase: The pdf_generator.py maps the structured JSON into an ATS-optimized HTML template.

Rendering Phase: The HTML template is converted into a finalized, download-ready PDF.

🚀 How to Run Locally
Clone the repository:

Bash
git clone https://github.com/Sahilhamids/ai-resume-tailor.git
cd ai-resume-tailor
Setup virtual environment:

Bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment:
Create a .env file and add your Gemini API Key:

Code snippet
API_KEY=your_gemini_api_key_here
Run the application:

Terminal 1 (Backend): uvicorn main:app --reload

Terminal 2 (Frontend): streamlit run app.py