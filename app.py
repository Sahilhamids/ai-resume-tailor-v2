# pyrefly: ignore [missing-import]
import streamlit as st
import requests
from pdf_generator import create_pdf_from_json

# 1. Set up the page layout
st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

st.title("📄 AI Resume Tailor")
st.write("Upload your base resume and paste the job description to get a tailored, ATS-friendly PDF!")

# 2. Create the input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Base Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste the exact Job Description here", height=150)

# 3. The Generate Button
if st.button("Tailor My Resume", type="primary"):
    
    # Check if user provided both inputs
    if uploaded_file is not None and job_description:
        with st.spinner("🤖 AI is analyzing and rewriting your resume... this takes a few seconds..."):
            
            # Prepare the files and data to send to FastAPI
            files = {"resume_file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            data = {"job_description": job_description}

            try:
                # 4. Call your FastAPI backend!
                response = requests.post("https://ai-resume-tailor-znxi.onrender.com/tailor-resume", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_data = result["ai_analysis"]
                    
                    # SECURITY CHECK: Verify the AI returned a valid dictionary
                    if ai_data and isinstance(ai_data, dict):
                        st.success("Resume successfully tailored and logged in the database!")
                        
                        # 5. Display the Interview Guidance on screen
                        st.subheader("💡 Interview Guidance & Skill Gaps")
                        st.info(ai_data.get("interview_guidance", "No guidance provided by AI."))
                        
                        # 6. Generate the PDF behind the scenes
                        pdf_filename = create_pdf_from_json(ai_data)
                        
                        if pdf_filename:
                            # 7. Provide the Download Button
                            with open(pdf_filename, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Tailored Resume PDF",
                                    data=pdf_file,
                                    file_name="Tailored_Resume_2026.pdf",
                                    mime="application/pdf"
                                )
                    else:
                        # Fallback if the AI made a JSON formatting mistake
                        st.error("🚨 The AI had a slight hiccup formatting your resume data. Please click 'Tailor My Resume' to try again!")
                        
                else:
                    st.error(f"Error from backend server: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Failed to connect to the backend server. Is your FastAPI server running in another terminal?")
    else:
        st.warning("⚠️ Please upload a resume and paste a job description first.")