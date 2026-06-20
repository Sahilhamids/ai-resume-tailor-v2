import streamlit as st
from extractor import extract_text_from_pdf
from ai_agent import analyze_resume
from sanitizer import sanitize_text
from database import init_db, save_audit, get_history_df
from validator import validate_missing_keywords

# Initialize the database when the app starts
init_db()

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

# --- FILE EXTRACTION & SANITIZATION LOGIC ---
if uploaded_file is not None:
    # Only re-extract if it's a new file
    if uploaded_file.name != st.session_state.last_uploaded_file:
        # 1. Extract raw text
        raw_text = extract_text_from_pdf(uploaded_file.getvalue())
        # 2. Sanitize PII (Emails/Phones) before saving to memory
        st.session_state.resume_text = sanitize_text(raw_text)
        st.session_state.last_uploaded_file = uploaded_file.name

# --- MAIN WORKSPACE (WITH TABS) ---
if st.session_state.resume_text and job_description:
    
    # Create two tabs: One for the tool, one for the history chart
    tab_audit, tab_history = st.tabs(["🔍 Audit Workspace", "📈 My Progress History"])
    
    with tab_audit:
        st.info("💡 Edit your text directly in this box based on the feedback below, then hit Re-Run!")
        
        # Editable text area populated by our session state
        edited_resume_text = st.text_area("Extracted & Sanitized Resume Text", value=st.session_state.resume_text, height=300)
        
        # Save any user edits back to the session state memory
        st.session_state.resume_text = edited_resume_text

        # The Loop Trigger
        if st.button("Run / Re-Run ATS Audit", type="primary"):
            with st.spinner("AI is analyzing your profile..."):
                try:
                    # Pass the edited text to the AI
                    analysis = analyze_resume(st.session_state.resume_text, job_description, role_level)
                    
                    # Save the result to our SQLite Database
                    save_audit(role_level, analysis['ats_score'])
                    
                    # Validate the AI's missing keyword claims
                    validation_results = validate_missing_keywords(
                        st.session_state.resume_text, 
                        analysis['missing_keywords']
                    )
                    
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
                    
                    st.divider()
                    st.subheader("🎯 Keyword Gap Analysis")
                    
                    # 1. Show the TRULY missing keywords
                    if validation_results["truly_missing"]:
                        st.error("🚨 Missing Keywords (Add these!): " + ", ".join(validation_results["truly_missing"]))
                    else:
                        st.success("✅ Excellent! You have included all critical keywords requested by the job description.")
                        
                    # 2. Show the False Alarms (AI Hallucinations)
                    if validation_results["false_alarms"]:
                        st.info(f"🤖 **AI Hallucination Detected:** The AI thought you were missing these, but our system found them in your text: **{', '.join(validation_results['false_alarms'])}**")
                    
                    st.divider()
                    st.subheader("✍️ Paraphrasing Suggestions")
                    st.table(analysis['paraphrasing_suggestions'])
                    
                except Exception as e:
                    st.error(f"Error connecting to AI Assistant: {e}")
                    
    with tab_history:
        st.header("Your ATS Score Progression")
        st.write("Track how your resume improves over time as you make edits.")
        
        # Fetch data from DB
        history_df = get_history_df()
        
        if not history_df.empty:
            # Create a line chart using the scores
            st.line_chart(history_df.set_index('timestamp')['score'])
            # Show the raw data table below it
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No history yet! Run your first audit to see your progress.")

elif not uploaded_file:
    st.warning("👈 Please upload a PDF resume to begin.")
elif not job_description:
    st.warning("👈 Please paste a Job Description to begin.")