# 📄 AI Resume Tailor (Full-Stack Web App)

## Overview
The AI Resume Tailor is a full-stack web application designed to solve a major bottleneck for job seekers: manually tailoring resumes for Applicant Tracking Systems (ATS). Users can upload their base resume (PDF) and paste a target Job Description. The application utilizes Google's Gemini AI to analyze the match, highlight relevant skills without hallucinating experience, and instantly generate a strictly ATS-friendly, single-column PDF resume.

**Live Demo:** [Click here to view the live application](https://ai-resume-tailor-app-by-sahil.streamlit.app/)

## 🚀 Features
* **Automated Tailoring:** Dynamically rewrites resume bullet points to align with specific Job Description keywords.
* **Skill Gap Analysis:** Provides users with a list of missing critical skills and a brief interview prep guide.
* **ATS-Friendly Export:** Bypasses complex HTML/CSS rendering to generate clean, single-column PDFs optimized for ATS parsers.
* **Database Logging:** Logs user queries and AI analyses into a relational database for analytics.

## 💻 Tech Stack
* **Frontend:** Streamlit (Python), hosted on Streamlit Community Cloud
* **Backend:** FastAPI, hosted on Render
* **AI Integration:** Google Gemini 2.5 Flash API (`google-genai` SDK)
* **Database:** SQLite3
* **PDF Generation:** `xhtml2pdf`, `Jinja2`
* **Data Parsing:** `PyPDF2`

## ⚙️ How It Works (Architecture)
1. **Client Interface:** The Streamlit frontend captures the user's PDF and text inputs and sends a `POST` request to the backend.
2. **Data Extraction:** The FastAPI backend uses PyPDF2 to extract raw text from the uploaded document.
3. **LLM Processing:** The text and job description are passed to the Gemini AI API with strict prompt engineering to force a structured JSON output.
4. **Data Mapping:** The backend uses Jinja2 to map the AI's JSON response into a minimalist, ATS-compliant HTML template.
5. **PDF Compilation:** `xhtml2pdf` converts the populated HTML template into a downloadable PDF binary.
6. **Logging:** The transaction details are stored via an SQL `INSERT` query into a local SQLite database.

## 🛠️ Local Setup
To run this project locally, you will need two separate terminal windows for the frontend and backend.

1. Clone the repository and create a virtual environment:
```bash
git clone [https://github.com/Sahilhamids/ai-resume-tailor.git](https://github.com/Sahilhamids/ai-resume-tailor.git)
cd ai-resume-tailor
python -m venv venv
venv\Scripts\activate  # Windows