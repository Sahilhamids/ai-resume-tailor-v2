# 🚀 Career Intelligence Platform

**Live demo: [https://ai-resume-tailor-v2.onrender.com/dashboard](https://ai-resume-tailor-v2.onrender.com/dashboard)**

An AI-powered career toolkit: upload a resume or describe your background, tailor it to a specific job, audit it against an ATS, generate a cover letter, and track your applications — all with no signup required.

## Features

- **No login required** — an anonymous session is issued automatically; your profile and history persist per-browser.
- **AI Onboarding** — upload an existing resume PDF and auto-fill your profile via Gemini/Groq.
- **Resume Builder** — tailors your profile to a job description, with 3 visual templates (Modern/Classic/Minimal), a live preview, and PDF/DOCX export.
- **Saved Resume Versions** — name and keep multiple tailored resumes for different roles.
- **ATS Auditor** — scores a resume against a job description, flags missing keywords (fact-checked against the raw text to catch AI hallucinations), and tracks score history with before/after comparison.
- **Cover Letter Generator** — strictly factual, generated from your saved profile data.
- **Job Application Tracker** — a Kanban board (Applied → Interviewing → Offer → Rejected).
- **Anti-hallucination prompting** — the AI is instructed never to invent metrics, employers, or skills not present in your data; a separate validator double-checks "missing keyword" claims against the raw resume text.
- **High-availability LLM routing** — Gemini primary, Groq/Llama-3 fallback if the primary fails or rate-limits.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, JWT auth (anonymous sessions)
- **Frontend:** React + Vite, served as static files from the FastAPI app
- **Database:** PostgreSQL (Supabase free tier)
- **AI:** Google Gemini (primary), Groq/Llama-3 (fallback)
- **Document processing:** PyMuPDF (PDF text extraction), xhtml2pdf (PDF export), python-docx (Word export)
- **Deployment:** Docker, deployable free on Render

## Local Development

1. Clone the repo and `cd resume_tailor_app`.
2. Backend:
   ```
   python -m venv venv
   venv\Scripts\activate   # or source venv/bin/activate on Linux/Mac
   pip install -r requirements.txt
   ```
3. Frontend:
   ```
   cd frontend
   npm install
   npm run build
   ```
4. Create a `.env` file in the project root:
   ```
   API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   DATABASE_URL=postgresql://...
   JWT_SECRET=a_random_secret
   ```
5. Run the app:
   ```
   uvicorn main:app --reload
   ```

## Deployment

The included `Dockerfile` builds the React frontend and Python backend into a single image (multi-stage build), and `render.yaml` configures it for Render's free web service tier. Set `API_KEY`, `GROQ_API_KEY`, `DATABASE_URL`, and `JWT_SECRET` as environment variables in the Render dashboard — never commit them.

⚠️ Don't commit `.env`, `*.db` files, or any API keys — `.gitignore` already covers these.

Developed by Sahil Shaikh
