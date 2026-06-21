import streamlit as st
import requests
from datetime import datetime
from extractor import extract_text_from_pdf
from sanitizer import sanitize_text
from validator import validate_missing_keywords
from ai_agent import analyze_resume, generate_tailored_resume, parse_resume_to_profile
from database import (
    init_db, create_user, verify_login, 
    get_profile, update_profile, 
    get_skills, add_skill, delete_skill, 
    get_employment, add_employment, delete_employment, update_employment_record,
    get_projects, add_project, delete_project, update_project_record,
    get_custom_sections, add_custom_section, delete_custom_section, update_custom_section_record,
    save_audit, get_history_df
)

# Initialize the relational database
init_db()

# Page configuration
st.set_page_config(page_title="Career Intelligence Platform", layout="wide", initial_sidebar_state="expanded")

# --- MODERN UI & ANIMATED BACKGROUND CSS INJECTION ---
st.markdown("""
    <style>
        /* Hide the Streamlit menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Hide ONLY the Deploy Button, ensuring the sidebar toggle remains visible! */
        .stDeployButton {display: none;}
        header {visibility: visible !important;}
        
        /* Animated Colorful Gradient Background */
        .stApp {
            background: linear-gradient(-45deg, #1e1b4b, #312e81, #1e3a8a, #0f172a) !important;
            background-size: 400% 400% !important;
            animation: gradientBG 15s ease infinite !important;
        }
        
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Make buttons look modern */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        /* Add hover animation and glow to primary buttons */
        .stButton>button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }
        
        /* Modernize input boxes */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
            border-radius: 8px !important;
        }
        
        /* Polish expanders with borders and shadows */
        div[data-testid="stExpander"] {
            border-radius: 8px !important;
            border: 1px solid #334155 !important;
            background-color: rgba(30, 41, 59, 0.7) !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        
        /* Clean up tab styling */
        button[data-baseweb="tab"] {
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. SESSION STATE (The App's Memory) ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def logout():
    """Clears the session and sends the user back to the login screen."""
    st.session_state.user_id = None
    st.rerun()

# --- 2. UNGATED AREA (Login & Signup) ---
if st.session_state.user_id is None:
    st.title("🚀 Career Intelligence Platform")
    st.subheader("Your AI-powered toolkit to beat the ATS and land interviews.")
    
    # Create two tabs for clean UI
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Log In", type="primary")
            
            if submit_login:
                user_id = verify_login(email, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_signup = st.form_submit_button("Create Account", type="primary")
            
            if submit_signup:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success = create_user(new_email, new_password)
                    if success:
                        st.success("Account created successfully! Please switch to the Log In tab.")
                    else:
                        st.error("An account with this email already exists.")

# --- 3. GATED AREA (The Main App) ---
else:
    # --- VISITOR COUNTER AT TOP RIGHT ---
    # We use a 5-to-1 ratio column to push the badge all the way to the right
    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
        st.markdown("<div style='text-align: right; margin-top: 10px;'><img src='https://visitor-badge.laobi.icu/badge?page_id=my_resume_ai_app.main' alt='visitors'></div>", unsafe_allow_html=True)

    # Build the authenticated navigation sidebar
    with st.sidebar:
        st.title("🧭 Navigation")
        
        # This radio button dictates what page is shown in the main workspace
        page = st.radio("Go to:", [
            "🏠 Dashboard (My Profile)", 
            "⚡ Build Resume (Pipeline 1)", 
            "🔍 Audit PDF (Pipeline 2)"
        ])

    # ==========================================
    # PAGE 1: MASTER PROFILE DASHBOARD
    # ==========================================
    if page == "🏠 Dashboard (My Profile)":
        st.title("🏠 Master Profile Dashboard")
        st.write("This data acts as the 'brain' for your AI Resume Builder. Keep it updated!")
        
        user_id = st.session_state.user_id 
        
        # --- AI ONBOARDING IMPORTER ---
        with st.expander("✨ Auto-Fill Profile from existing Resume (PDF)"):
            st.info("Save time! Upload your current resume and let AI extract your data into your Master Profile.")
            import_file = st.file_uploader("Upload PDF to Import", type="pdf", key="import_uploader")
            
            if import_file and st.button("Extract & Populate Profile", type="primary"):
                with st.spinner("AI is reading your resume and populating your database..."):
                    try:
                        raw_text = extract_text_from_pdf(import_file.getvalue())
                        extracted_data = parse_resume_to_profile(raw_text)
                        
                        b_info = extracted_data.get("basic_info", {})
                        update_profile(
                            user_id, 
                            b_info.get("full_name", ""), 
                            b_info.get("phone", ""), 
                            b_info.get("linkedin_url", ""), 
                            b_info.get("github_url", ""), 
                            b_info.get("target_role", "")
                        )
                        
                        for skill in extracted_data.get("skills", []):
                            add_skill(user_id, skill)
                            
                        for job in extracted_data.get("employment", []):
                            add_employment(
                                user_id, 
                                job.get("company", ""), 
                                job.get("title", ""), 
                                job.get("start_date", ""), 
                                job.get("end_date", ""), 
                                job.get("responsibilities", "")
                            )
                            
                        for proj in extracted_data.get("projects", []):
                            add_project(
                                user_id, 
                                proj.get("name", ""), 
                                proj.get("description", ""), 
                                proj.get("link", "")
                            )
                            
                        st.success("✅ Profile successfully auto-populated!")
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Failed to parse resume: {e}")
        
        st.divider()

        profile = get_profile(user_id)
        
        # Streamlit Layout: 2 Columns
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            # --- 1. BASIC INFO ---
            st.subheader("👤 Basic Information")
            with st.form("profile_form"):
                f_name = st.text_input("Full Name", value=profile[0] if profile[0] else "")
                f_phone = st.text_input("Phone Number", value=profile[1] if profile[1] else "")
                f_linkedin = st.text_input("LinkedIn URL", value=profile[2] if profile[2] else "")
                f_github = st.text_input("GitHub/Portfolio URL", value=profile[3] if profile[3] else "")
                f_role = st.text_input("Current Target Role", value=profile[4] if profile[4] else "")
                
                if st.form_submit_button("Save Profile Info", type="primary"):
                    update_profile(user_id, f_name, f_phone, f_linkedin, f_github, f_role)
                    st.success("Profile updated!")
                    st.rerun()

            st.divider()
            
            # --- 2. EMPLOYMENT HISTORY ---
            st.subheader("💼 Employment History")
            jobs = get_employment(user_id)
            for job in jobs:
                with st.expander(f"✏️ Edit: {job[2]} at {job[1]} ({job[3]} - {job[4]})"):
                    with st.form(f"edit_job_{job[0]}"):
                        e_comp = st.text_input("Company Name", value=job[1])
                        e_role = st.text_input("Job Title", value=job[2])
                        col1, col2 = st.columns(2)
                        e_start = col1.text_input("Start Date", value=job[3])
                        e_end = col2.text_input("End Date", value=job[4])
                        e_resp = st.text_area("Responsibilities", value=job[5], height=150)
                        
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            update_employment_record(job[0], e_comp, e_role, e_start, e_end, e_resp)
                            st.rerun()
                            
                    if st.button("🗑️ Delete Experience", key=f"del_job_{job[0]}"):
                        delete_employment(job[0])
                        st.rerun()
            
            with st.expander("➕ Add New Work Experience"):
                with st.form("add_job_form"):
                    j_company = st.text_input("Company Name")
                    j_role = st.text_input("Job Title")
                    col1, col2 = st.columns(2)
                    j_start = col1.text_input("Start Date (MM/YYYY)")
                    j_end = col2.text_input("End Date (MM/YYYY or 'Present')")
                    j_resp = st.text_area("Responsibilities & Achievements")
                    
                    if st.form_submit_button("Save Experience", type="primary"):
                        add_employment(user_id, j_company, j_role, j_start, j_end, j_resp)
                        st.rerun()

            st.divider()

            # --- 3. PROJECTS SECTION ---
            st.subheader("🚀 Projects")
            projects = get_projects(user_id)
            for proj in projects:
                with st.expander(f"✏️ Edit: {proj[1]}"):
                    with st.form(f"edit_proj_{proj[0]}"):
                        p_name_e = st.text_input("Project Name", value=proj[1])
                        p_link_e = st.text_input("Live Link / GitHub", value=proj[3])
                        p_desc_e = st.text_area("Description", value=proj[2], height=100)
                        
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            update_project_record(proj[0], p_name_e, p_desc_e, p_link_e)
                            st.rerun()
                            
                    if st.button("🗑️ Delete Project", key=f"del_proj_{proj[0]}"):
                        delete_project(proj[0])
                        st.rerun()

            with st.expander("➕ Add New Project"):
                with st.form("add_project_form"):
                    p_name = st.text_input("Project Name")
                    p_link = st.text_input("Live Link / GitHub Repo")
                    p_desc = st.text_area("Project Description & Tech Stack used")
                    if st.form_submit_button("Save Project", type="primary"):
                        add_project(user_id, p_name, p_desc, p_link)
                        st.rerun()

            st.divider()

            # --- 4. CUSTOM SECTIONS ---
            st.subheader("📌 Other Sections")
            custom_sections = get_custom_sections(user_id)
            for sec in custom_sections:
                with st.expander(f"✏️ Edit: {sec[1]}"):
                    with st.form(f"edit_sec_{sec[0]}"):
                        c_title_e = st.text_input("Title", value=sec[1])
                        c_content_e = st.text_area("Content", value=sec[2], height=100)
                        
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            update_custom_section_record(sec[0], c_title_e, c_content_e)
                            st.rerun()
                            
                    if st.button("🗑️ Delete Section", key=f"del_sec_{sec[0]}"):
                        delete_custom_section(sec[0])
                        st.rerun()

            with st.expander("➕ Add Custom Section"):
                with st.form("add_custom_section_form"):
                    c_title = st.text_input("Section Title")
                    c_content = st.text_area("Section Content")
                    if st.form_submit_button("Save Section", type="primary"):
                        add_custom_section(user_id, c_title, c_content)
                        st.rerun()

        with col_side:
            # --- 5. SKILLS INVENTORY ---
            st.subheader("🛠️ Skills Inventory")
            skills = get_skills(user_id)
            
            if skills:
                st.info(", ".join([s[1] for s in skills]))
                with st.form("delete_skill_form"):
                    st.write("Remove a skill:")
                    skill_to_delete = st.selectbox("Select skill", options=skills, format_func=lambda x: x[1])
                    if st.form_submit_button("🗑️ Remove") and skill_to_delete:
                        delete_skill(skill_to_delete[0])
                        st.rerun()
            else:
                st.warning("No skills added yet.")
                
            with st.form("add_skill_form"):
                new_skill = st.text_input("Add a Skill")
                if st.form_submit_button("Add Skill", type="primary") and new_skill:
                    add_skill(user_id, new_skill)
                    st.rerun()

    # ==========================================
    # PAGE 2: RESUME BUILDER (PIPELINE 1)
    # ==========================================
    elif page == "⚡ Build Resume (Pipeline 1)":
        st.title("⚡ Dynamic Resume Builder")
        st.write("Paste a Job Description here. The AI will securely pull your data from the Master Profile and write perfect, ATS-optimized resume sections for you to copy and paste.")
        
        user_id = st.session_state.user_id
        
        profile = get_profile(user_id)
        jobs = get_employment(user_id)
        projects = get_projects(user_id)
        skills = get_skills(user_id)
        
        if not profile or not profile[0]:
            st.warning("⚠️ Your Master Profile is mostly empty! Please go to the Dashboard and fill out your basic info and work history first.")
        else:
            jd_input = st.text_area("Paste the Target Job Description here:", height=250)
            
            if st.button("Generate Tailored Resume Content", type="primary") and jd_input:
                with st.spinner("Compiling your profile and consulting the AI..."):
                    
                    compiled_profile = f"Target Role: {profile[4]}\n\n"
                    compiled_profile += "SKILLS:\n" + ", ".join([s[1] for s in skills]) + "\n\n"
                    
                    compiled_profile += "EMPLOYMENT HISTORY:\n"
                    for j in jobs:
                        compiled_profile += f"- {j[2]} at {j[1]} ({j[3]} to {j[4]}):\n  Responsibilities: {j[5]}\n\n"
                        
                    compiled_profile += "PROJECTS:\n"
                    for p in projects:
                        compiled_profile += f"- {p[1]}: {p[2]}\n\n"
                        
                    try:
                        generated_resume = generate_tailored_resume(compiled_profile, jd_input)
                        
                        st.success("✅ Resume content successfully generated! Copy the text below into your document template.")
                        
                        st.divider()
                        st.subheader("📝 Professional Summary")
                        st.write(generated_resume.get("professional_summary", ""))
                        
                        st.subheader("💼 Tailored Work Experience")
                        for exp in generated_resume.get("tailored_employment", []):
                            st.markdown(f"**{exp.get('title', '')}** | {exp.get('company', '')} | *{exp.get('duration', '')}*")
                            for bullet in exp.get("optimized_bullets", []):
                                st.markdown(f"- {bullet}")
                            st.write("") 
                                
                        st.subheader("🚀 Tailored Projects")
                        for proj in generated_resume.get("tailored_projects", []):
                            st.markdown(f"**{proj.get('name', '')}**")
                            st.write(proj.get("optimized_description", ""))
                            st.write("") 
                            
                        st.subheader("🛠️ Top Relevant Skills")
                        st.write(", ".join(generated_resume.get("top_relevant_skills", [])))
                        
                    except Exception as e:
                        st.error(f"Error generating resume: {e}")
                        
    # ==========================================
    # PAGE 3: RESUME AUDITOR (PIPELINE 2)
    # ==========================================
    elif page == "🔍 Audit PDF (Pipeline 2)":
        st.title("🔍 ATS Resume Auditor")
        st.write("Upload an existing PDF to check its score against a Job Description. Your history is saved to your account.")
        
        user_id = st.session_state.user_id

        # --- Sidebar Inputs ---
        with st.sidebar:
            st.header("1. Upload & Setup")
            uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
            job_description = st.text_area("Job Description", height=200)
            role_level = st.text_input("Target Role", value="Software Engineer")

        # --- Memory State ---
        if "resume_text" not in st.session_state:
            st.session_state.resume_text = ""
        if "last_uploaded_file" not in st.session_state:
            st.session_state.last_uploaded_file = None

        # --- File Extraction & Sanitization ---
        if uploaded_file is not None:
            if uploaded_file.name != st.session_state.last_uploaded_file:
                raw_text = extract_text_from_pdf(uploaded_file.getvalue())
                st.session_state.resume_text = sanitize_text(raw_text)
                st.session_state.last_uploaded_file = uploaded_file.name

        # --- Main Workspace ---
        if st.session_state.resume_text and job_description:
            tab_audit, tab_history = st.tabs(["🔍 Audit Workspace", "📈 My Progress History"])
            
            with tab_audit:
                st.info("💡 Edit your text directly in this box based on the feedback below, then hit Re-Run!")
                edited_resume_text = st.text_area("Extracted & Sanitized Resume Text", value=st.session_state.resume_text, height=300)
                st.session_state.resume_text = edited_resume_text

                if st.button("Run / Re-Run ATS Audit", type="primary"):
                    with st.spinner("AI is analyzing your profile..."):
                        try:
                            analysis = analyze_resume(st.session_state.resume_text, job_description, role_level)
                            
                            save_audit(user_id, role_level, analysis['ats_score'])
                            
                            validation_results = validate_missing_keywords(
                                st.session_state.resume_text, 
                                analysis['missing_keywords']
                            )
                            
                            st.divider()
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
                            if validation_results["truly_missing"]:
                                st.error("🚨 Missing Keywords: " + ", ".join(validation_results["truly_missing"]))
                            else:
                                st.success("✅ Excellent! All critical keywords included.")
                                
                            if validation_results["false_alarms"]:
                                st.info(f"🤖 **AI Hallucination Detected:** {', '.join(validation_results['false_alarms'])}")
                            
                            st.divider()
                            st.subheader("✍️ Paraphrasing Suggestions")
                            st.table(analysis['paraphrasing_suggestions'])
                            
                        except Exception as e:
                            st.error(f"Error connecting to AI: {e}")
                            
            with tab_history:
                st.header("Your Personal ATS Score Progression")
                history_df = get_history_df(user_id)
                
                if not history_df.empty:
                    st.line_chart(history_df.set_index('timestamp')['score'])
                    st.dataframe(history_df, use_container_width=True)
                else:
                    st.info("No history yet! Run your first audit to see your progress.")
                    
        elif not uploaded_file:
            st.warning("👈 Please upload a PDF resume to begin.")
        elif not job_description:
            st.warning("👈 Please paste a Job Description in the sidebar to begin.")


    # ==========================================
    # GLOBAL FOOTER (Displays at the bottom of EVERY authenticated page)
    # ==========================================
    st.write("")
    st.write("")
    st.markdown("---")
    
    # Split the footer into two clean columns
    foot_col1, foot_col2 = st.columns(2)
    
    with foot_col1:
        st.markdown("###Developed By")
        st.markdown("**SAHIL SHAIKH**") # <--- UPDATE THIS
        st.markdown("[🔗 LinkedIn](https://linkedin.com/in/sahil-h-shaikh) | [📸 Instagram](https://www.instagram.com/s.sahilhamid/)") # <--- UPDATE THIS
        
    with foot_col2:
        current_time = datetime.now().strftime("%I:%M %p")
        try:
            weather_req = requests.get("https://wttr.in/?format=3", timeout=3)
            weather = weather_req.text.strip()
        except:
            weather = "Weather unavailable"
        st.info(f"🕒 **Current Time:** {current_time}  \n🌤️ **Weather:** {weather}")
        
        st.write("")
        if st.button("🚪 Log Out", type="secondary"):
            logout()