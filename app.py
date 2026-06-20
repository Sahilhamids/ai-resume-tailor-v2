import streamlit as st
import requests
from pdf_generator import create_pdf_from_json
import time

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄")
st.title("📄 AI Resume Tailor")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
job_description = st.text_area("Job Description")

if st.button("Tailor My Resume Now", type="primary"):
    if uploaded_file and job_description:
        with st.spinner("🤖 AI is analyzing..."):
            files = {"resume_file": uploaded_file.getvalue()}
            data = {"job_description": job_description}
            try:
                response = requests.post("[https://YOUR-RENDER-URL.onrender.com/tailor-resume](https://YOUR-RENDER-URL.onrender.com/tailor-resume)", files=files, data=data)
                if response.status_code == 200:
                    ai_data = response.json().get("ai_analysis")
                    if isinstance(ai_data, dict):
                        st.success("Resume tailored!")
                        st.info(ai_data.get("interview_guidance", "Guidance ready."))
                        pdf_path = create_pdf_from_json(ai_data)
                        with open(pdf_path, "rb") as f:
                            st.download_button("Download PDF", f, "Tailored_Resume.pdf")
                    else:
                        st.error("🚨 Formatting hiccup. Try again.")
                else:
                    st.error("Backend Error.")
            except Exception as e:
                st.error(f"Connection Error: {e}")