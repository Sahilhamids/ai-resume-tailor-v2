# pyrefly: ignore [missing-import]
import streamlit as st
import requests
from pdf_generator import create_pdf_from_json
import time

# 1. Set up the page layout
st.set_page_config(page_title="AI Resume Tailor", page_icon="🚀", layout="wide")

# Inject Custom CSS for Animations and Polish
st.markdown("""
    <style>
    /* Add a smooth fade-in animation to the main container */
    .main {
        animation: fadeIn 1.5s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Make the primary button pulse to draw attention */
    .stButton>button {
        transition: all 0.3s ease 0s;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 8px 20px rgba(0, 200, 150, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 AI Resume Tailor Pro")
st.write("Upload your base resume and paste the job description to get a tailored, single-page, ATS-friendly PDF!")

# 2. Create the input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. Upload Base Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

with col2:
    st.subheader("🎯 2. Job Description")
    job_description = st.text_area("Paste the exact Job Description here", height=150)

# 3. The Generate Button
if st.button("✨ Tailor My Resume Now", type="primary", use_container_width=True):
    
    if uploaded_file is not None and job_description:
        # Use an animated status container instead of a boring spinner
        with st.status("🤖 Initiating AI Engine...", expanded=True) as status:
            st.write("📄 Extracting text from your PDF...")
            time.sleep(1) # Small visual delay for effect
            st.write("🧠 Connecting to Gemini AI for analysis...")
            
            files = {"resume_file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            data = {"job_description": job_description}

            try:
                # IMPORTANT: Keep your specific Render URL here!
                response = requests.post("https://ai-resume-tailor-znxi.onrender.com/tailor-resume", files=files, data=data, timeout=120)
                if response.status_code == 200:
                    st.write("✍️ Generating 1-page PDF layout...")
                    result = response.json()
                    ai_data = result["ai_analysis"]
                    
                    if ai_data and isinstance(ai_data, dict):
                        status.update(label="✅ Resume Successfully Tailored!", state="complete", expanded=False)
                        
                        # Trigger visual animations!
                        st.balloons()
                        st.toast('PDF Generated Successfully!', icon='🎉')
                        
                        st.subheader("💡 Interview Guidance & Skill Gaps")
                        st.info(ai_data.get("interview_guidance", "No guidance provided by AI."))
                        
                        pdf_filename = create_pdf_from_json(ai_data)
                        
                        if pdf_filename:
                            with open(pdf_filename, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Your 1-Page Resume PDF",
                                    data=pdf_file,
                                    file_name="Tailored_Resume_Pro.pdf",
                                    mime="application/pdf",
                                    type="primary",
                                    use_container_width=True
                                )
                    else:
                        status.update(label="🚨 AI Formatting Error", state="error")
                        st.error("The AI had a slight hiccup formatting your resume data. Please try again!")
                        
                else:
                    status.update(label="🚨 Backend Error", state="error")
                    st.error(f"Error from backend server: {response.text}")
            except requests.exceptions.ConnectionError:
                status.update(label="🚨 Connection Error", state="error")
                st.error("Failed to connect to the backend server. Is your Render API awake?")
    else:
        st.warning("⚠️ Please upload a resume and paste a job description first.")