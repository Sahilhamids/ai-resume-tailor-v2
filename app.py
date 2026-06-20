# pyrefly: ignore [missing-import]
import streamlit as st
from extractor import extract_text_from_pdf
from ai_agent import analyze_resume
from sanitizer import sanitize_text

st.set_page_config(page_title="AI Resume Auditor", layout="wide")
st.title("📊 AI Resume Auditor")

# --- STATE MANAGEMENT ---
# Initialize session state to act as our app's "memory"
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("1. Upload & Setup")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    job_description = st.text_area("Job Description", height=200)
    role_level = st.text_input("Target Role", value="Software Engineer")

# --- FILE EXTRACTION LOGIC ---
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.last_uploaded_file:
        
        # 1. Extract the raw text
        raw_text = extract_text_from_pdf(uploaded_file.getvalue())
        
        # 2. Sanitize it before saving to memory!
        st.session_state.resume_text = sanitize_text(raw_text)
        
        st.session_state.last_uploaded_file = uploaded_file.name

# --- MAIN WORKSPACE (The Loop) ---
if st.session_state.resume_text and job_description:
    st.header("2. Iterative Optimization Workspace")
    
    st.info("💡 Edit your text directly in this box based on the feedback below, then hit Re-Run!")
    
    # Editable text area populated by our session state
    edited_resume_text = st.text_area("Extracted Resume Text", value=st.session_state.resume_text, height=300)
    
    # Save any user edits back to the session state memory
    st.session_state.resume_text = edited_resume_text

    # The Loop Trigger
    if st.button("Run / Re-Run ATS Audit", type="primary"):
        with st.spinner("AI is analyzing your profile..."):
            try:
                # IMPORTANT: We pass the EDITED text to the AI, not the original PDF
                analysis = analyze_resume(st.session_state.resume_text, job_description, role_level)
                
                st.divider()
                st.header("3. Audit Results")
                
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
                st.error(", ".join(analysis['missing_keywords']))
                
                st.subheader("✍️ Paraphrasing Suggestions")
                st.table(analysis['paraphrasing_suggestions'])
                
            except Exception as e:
                st.error(f"Error: {e}")
elif not uploaded_file:
    st.warning("👈 Please upload a PDF resume to begin.")
elif not job_description:
    st.warning("👈 Please paste a Job Description to begin.")