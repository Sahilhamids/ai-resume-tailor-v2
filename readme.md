🚀 Career Intelligence Platform (AI Resume SaaS)

A full-stack, AI-powered Software-as-a-Service (SaaS) application designed to help job seekers beat the Applicant Tracking System (ATS).

Unlike basic AI wrappers, this platform features secure user authentication, a persistent relational database for managing career profiles, and strict, hallucination-free LLM prompt engineering to generate factual, copy-paste-ready resume content tailored to specific Job Descriptions.

Check it out here: https://ai-resume-tailor-v2.streamlit.app/
✨ Key Features

🔐 Secure Authentication & User State: Implemented bcrypt password hashing and Streamlit session state to create a secure, gated multi-user environment.

💾 Persistent Relational Database: Engineered a full CRUD (Create, Read, Update, Delete) SQLite database to act as the user's "Master Profile," storing employment history, skills, projects, and custom sections securely.

🪄 AI Onboarding (Cold-Start Resolution): Users can upload an existing PDF resume, and the AI will extract, parse, and auto-populate the database using strict JSON schemas.

⚡ Pipeline 1 (Dynamic Builder): Cross-references the user's factual database profile with a target Job Description to generate highly optimized, tailored resume bullets. Strict system prompts prevent AI hallucinations (inventing metrics or fake jobs).

🔍 Pipeline 2 (ATS Auditor): Extracts and sanitizes text from uploaded PDFs, scores it against a Job Description, performs keyword gap analysis, and tracks the user's score progression over time via a historical database.

🔀 High-Availability LLM Architecture: Implemented an API fallback cascade. If the primary model (Google Gemini) fails or rate-limits, the system automatically seamlessly cascades to a secondary high-speed model (Llama-3.1 via Groq).

🎨 Modern UI/UX: Custom CSS injection overrides default Streamlit styling to provide a sleek, dark-mode SaaS aesthetic with glassmorphic containers, an animated gradient background, real-time weather, and visitor tracking widgets.

🛠️ Tech Stack

Frontend: Streamlit, Custom CSS, HTML

Backend: Python

Database: SQLite3, Pandas (for data visualization)

AI / LLMs: Google Gemini API (Primary), Groq API / Llama-3.1 (Fallback)

Document Processing: PyMuPDF (fitz)

Security & Utilities: bcrypt, requests, datetime

🏗️ System Architecture

app.py: The main routing engine and UI layer. Manages session state, authentication UI, global modern CSS, and multi-page navigation.

database.py: Handles all SQLite connections, user creation, password verification, and complex CRUD operations for user profiles and audit histories.

ai_agent.py: The AI engine. Manages API connections, fallback logic, and strict JSON-enforced prompt engineering.

extractor.py & sanitizer.py: Text processing layer ensuring raw PDFs are cleaned of hidden characters and ligatures before being sent to the LLM context window.

validator.py: A deterministic regex engine that double-checks the AI's keyword analysis to prevent "AI False Alarms."

💻 Installation & Local Setup

1. Clone the repository

git clone [https://github.com/Sahilhamids/ai-resume-tailor-v2.git](https://github.com/yourusername/career-intelligence-platform.git)
cd career-intelligence-platform


2. Create a virtual environment and install dependencies

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt


3. Configure API Secrets
Create a .streamlit folder in the root directory, and inside it, create a secrets.toml file. Add your API keys:

API_KEY = "your_google_gemini_key_here"
GROQ_API_KEY = "your_groq_key_here"


4. Run the application

streamlit run app.py


⚠️ Important Note on Deployment

If deploying to Streamlit Community Cloud or Render, ensure you do not commit your .streamlit/secrets.toml file or your .db SQLite files. Use a .gitignore file to keep them private.

📈 Future Roadmap

Integration with a FastAPI backend for decoupling the UI.

PDF generation (exporting the tailored text directly into a formatted PDF layout).

LinkedIn URL scraping to auto-populate the master profile without a PDF.

Developed by SAHIL SHAIKH
