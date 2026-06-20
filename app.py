import streamlit as st
from extractor import extract_text_from_pdf
from ai_agent import analyze_resume

st.set_page_config(page_title="AI Resume Auditor", layout="wide")
st.title("📊 AI Resume Auditor")
st.markdown("Upload your resume and paste a Job Description to get an ATS-ready audit.")

# Input Section
with st.sidebar:
    st.header("Inputs")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    job_description = st.text_area("Job Description", height=200)
    role_level = st.selectbox("Target Role Level", ["Intern", "Junior", "Senior", "Staff"])
    submit = st.button("Run ATS Audit", type="primary")

# Execution Logic
if submit and uploaded_file and job_description:
    with st.spinner("AI is analyzing your profile..."):
        try:
            resume_text = extract_text_from_pdf(uploaded_file.getvalue())
            analysis = analyze_resume(resume_text, job_description, role_level)
            
            # Dashboard Display
            st.metric("ATS Compatibility Score", f"{analysis['ats_score']}%")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Strengths")
                for s in analysis['strengths']: st.write(f"• {s}")
            with col2:
                st.subheader("⚠️ Weaknesses")
                for w in analysis['weaknesses']: st.write(f"• {w}")
            
            st.subheader("🎯 Missing Keywords")
            st.info(", ".join(analysis['missing_keywords']))
            
            st.subheader("✍️ Paraphrasing Suggestions")
            st.table(analysis['paraphrasing_suggestions'])
            
        except Exception as e:
            st.error(f"Error: {e}")