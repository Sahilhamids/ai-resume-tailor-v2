import bcrypt
from datetime import datetime

from db import (
    get_session, User, Profile, EmploymentHistory, Education, Skill, Project, CustomSection, Audit,
    SavedResume, CoverLetter, JobApplication, UsageEvent,
)

# --- AUTHENTICATION LOGIC ---

def create_user(email, password):
    """Securely hashes the password and creates a new user."""
    session = get_session()
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

        user = User(email=email, password_hash=hashed.decode("utf-8"), created_at=datetime.utcnow())
        session.add(user)
        session.flush()

        session.add(Profile(user_id=user.id))
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def verify_login(email, password):
    """Verifies credentials and returns the user_id if successful."""
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return user.id
        return None
    finally:
        session.close()


def get_user_email(user_id):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user.email if user else None
    finally:
        session.close()


def set_user_credentials(user_id, email, password):
    """Links a real email/password to an existing (typically anonymous) user, so
    they can log back in from another device. Returns False if the email is taken."""
    session = get_session()
    try:
        existing = session.query(User).filter(User.email == email, User.id != user_id).first()
        if existing:
            return False
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        session.query(User).filter(User.id == user_id).update({
            "email": email,
            "password_hash": hashed.decode("utf-8"),
        })
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def delete_user(user_id):
    session = get_session()
    try:
        session.query(User).filter(User.id == user_id).delete()
        session.commit()
    finally:
        session.close()


# --- PROFILE & DATA CRUD OPERATIONS ---

def get_profile(user_id):
    """Fetches the user's basic profile information."""
    session = get_session()
    try:
        p = session.query(Profile).filter(Profile.user_id == user_id).first()
        if not p:
            return None
        return (p.full_name, p.phone, p.linkedin_url, p.github_url, p.target_role)
    finally:
        session.close()


def update_profile(user_id, full_name, phone, linkedin, github, target_role):
    """Updates the user's basic profile."""
    session = get_session()
    try:
        session.query(Profile).filter(Profile.user_id == user_id).update({
            "full_name": full_name,
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
            "target_role": target_role,
        })
        session.commit()
    finally:
        session.close()


def get_skills(user_id):
    """Fetches all skills for a user."""
    session = get_session()
    try:
        rows = session.query(Skill).filter(Skill.user_id == user_id).all()
        return [(s.id, s.skill_name) for s in rows]
    finally:
        session.close()


def add_skill(user_id, skill_name):
    """Adds a new skill to the user's profile."""
    session = get_session()
    try:
        session.add(Skill(user_id=user_id, skill_name=skill_name))
        session.commit()
    finally:
        session.close()


def get_employment(user_id):
    """Fetches employment history for a user."""
    session = get_session()
    try:
        rows = session.query(EmploymentHistory).filter(EmploymentHistory.user_id == user_id).all()
        return [(j.id, j.company_name, j.role_title, j.start_date, j.end_date, j.responsibilities) for j in rows]
    finally:
        session.close()


def add_employment(user_id, company, role, start_date, end_date, responsibilities):
    """Adds a new job to the employment history."""
    session = get_session()
    try:
        session.add(EmploymentHistory(
            user_id=user_id, company_name=company, role_title=role,
            start_date=start_date, end_date=end_date, responsibilities=responsibilities,
        ))
        session.commit()
    finally:
        session.close()


# --- EDUCATION CRUD ---

def get_education(user_id):
    session = get_session()
    try:
        rows = session.query(Education).filter(Education.user_id == user_id).all()
        return [(e.id, e.institution, e.degree, e.field_of_study, e.start_year, e.end_year, e.grade) for e in rows]
    finally:
        session.close()


def add_education(user_id, institution, degree, field_of_study, start_year, end_year, grade):
    session = get_session()
    try:
        session.add(Education(
            user_id=user_id, institution=institution, degree=degree,
            field_of_study=field_of_study, start_year=start_year, end_year=end_year, grade=grade,
        ))
        session.commit()
    finally:
        session.close()


def delete_education(edu_id):
    session = get_session()
    try:
        session.query(Education).filter(Education.id == edu_id).delete()
        session.commit()
    finally:
        session.close()


# --- PROJECTS & CUSTOM SECTIONS CRUD ---

def get_projects(user_id):
    """Fetches all projects for a user."""
    session = get_session()
    try:
        rows = session.query(Project).filter(Project.user_id == user_id).all()
        return [(p.id, p.project_name, p.description, p.link) for p in rows]
    finally:
        session.close()


def add_project(user_id, name, description, link):
    """Adds a new project."""
    session = get_session()
    try:
        session.add(Project(user_id=user_id, project_name=name, description=description, link=link))
        session.commit()
    finally:
        session.close()


def get_custom_sections(user_id):
    """Fetches custom sections (e.g., Certifications)."""
    session = get_session()
    try:
        rows = session.query(CustomSection).filter(CustomSection.user_id == user_id).all()
        return [(c.id, c.section_title, c.content) for c in rows]
    finally:
        session.close()


def add_custom_section(user_id, title, content):
    """Adds a new custom section."""
    session = get_session()
    try:
        session.add(CustomSection(user_id=user_id, section_title=title, content=content))
        session.commit()
    finally:
        session.close()


# --- AUDIT HISTORY CRUD ---

def save_audit(user_id, target_role, score):
    """Saves a new audit result to the user's history."""
    session = get_session()
    try:
        session.add(Audit(user_id=user_id, timestamp=datetime.utcnow(), target_role=target_role, score=score))
        session.commit()
    finally:
        session.close()


def get_history(user_id):
    """Fetches the user's audit history as a list of dicts, ordered oldest to newest."""
    session = get_session()
    try:
        rows = (
            session.query(Audit)
            .filter(Audit.user_id == user_id)
            .order_by(Audit.timestamp.asc())
            .all()
        )
        return [
            {"timestamp": a.timestamp.isoformat(), "target_role": a.target_role, "score": a.score}
            for a in rows
        ]
    finally:
        session.close()


# --- UPDATE & DELETE OPERATIONS ---

def delete_employment(job_id):
    session = get_session()
    try:
        session.query(EmploymentHistory).filter(EmploymentHistory.id == job_id).delete()
        session.commit()
    finally:
        session.close()


def update_employment_record(job_id, company, role, start, end, resp):
    session = get_session()
    try:
        session.query(EmploymentHistory).filter(EmploymentHistory.id == job_id).update({
            "company_name": company,
            "role_title": role,
            "start_date": start,
            "end_date": end,
            "responsibilities": resp,
        })
        session.commit()
    finally:
        session.close()


def delete_project(project_id):
    session = get_session()
    try:
        session.query(Project).filter(Project.id == project_id).delete()
        session.commit()
    finally:
        session.close()


def update_project_record(project_id, name, desc, link):
    session = get_session()
    try:
        session.query(Project).filter(Project.id == project_id).update({
            "project_name": name,
            "description": desc,
            "link": link,
        })
        session.commit()
    finally:
        session.close()


def delete_custom_section(section_id):
    session = get_session()
    try:
        session.query(CustomSection).filter(CustomSection.id == section_id).delete()
        session.commit()
    finally:
        session.close()


def update_custom_section_record(section_id, title, content):
    session = get_session()
    try:
        session.query(CustomSection).filter(CustomSection.id == section_id).update({
            "section_title": title,
            "content": content,
        })
        session.commit()
    finally:
        session.close()


def delete_skill(skill_id):
    session = get_session()
    try:
        session.query(Skill).filter(Skill.id == skill_id).delete()
        session.commit()
    finally:
        session.close()


# --- SAVED RESUMES CRUD ---

def save_resume(user_id, title, job_description, template, result_json):
    session = get_session()
    try:
        r = SavedResume(
            user_id=user_id, title=title, job_description=job_description,
            template=template, result_json=result_json, created_at=datetime.utcnow(),
        )
        session.add(r)
        session.commit()
        return r.id
    finally:
        session.close()


def get_saved_resumes(user_id):
    session = get_session()
    try:
        rows = (
            session.query(SavedResume)
            .filter(SavedResume.user_id == user_id)
            .order_by(SavedResume.created_at.desc())
            .all()
        )
        return [
            {"id": r.id, "title": r.title, "job_description": r.job_description,
             "template": r.template, "created_at": r.created_at.isoformat()}
            for r in rows
        ]
    finally:
        session.close()


def get_saved_resume(resume_id):
    session = get_session()
    try:
        r = session.query(SavedResume).filter(SavedResume.id == resume_id).first()
        if not r:
            return None
        return {
            "id": r.id, "title": r.title, "job_description": r.job_description,
            "template": r.template, "result_json": r.result_json, "created_at": r.created_at.isoformat(),
        }
    finally:
        session.close()


def delete_saved_resume(resume_id):
    session = get_session()
    try:
        session.query(SavedResume).filter(SavedResume.id == resume_id).delete()
        session.commit()
    finally:
        session.close()


# --- COVER LETTERS CRUD ---

def save_cover_letter(user_id, title, company_name, content, saved_resume_id=None):
    session = get_session()
    try:
        c = CoverLetter(
            user_id=user_id, title=title, company_name=company_name, content=content,
            saved_resume_id=saved_resume_id, created_at=datetime.utcnow(),
        )
        session.add(c)
        session.commit()
        return c.id
    finally:
        session.close()


def get_cover_letters(user_id):
    session = get_session()
    try:
        rows = (
            session.query(CoverLetter)
            .filter(CoverLetter.user_id == user_id)
            .order_by(CoverLetter.created_at.desc())
            .all()
        )
        return [
            {"id": c.id, "title": c.title, "company_name": c.company_name,
             "content": c.content, "created_at": c.created_at.isoformat()}
            for c in rows
        ]
    finally:
        session.close()


def delete_cover_letter(cover_letter_id):
    session = get_session()
    try:
        session.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).delete()
        session.commit()
    finally:
        session.close()


# --- JOB APPLICATION TRACKER CRUD ---

def add_job_application(user_id, company, role, status="applied", notes="", saved_resume_id=None):
    session = get_session()
    try:
        now = datetime.utcnow()
        j = JobApplication(
            user_id=user_id, company=company, role=role, status=status, notes=notes,
            saved_resume_id=saved_resume_id, created_at=now, updated_at=now,
        )
        session.add(j)
        session.commit()
        return j.id
    finally:
        session.close()


def get_job_applications(user_id):
    session = get_session()
    try:
        rows = (
            session.query(JobApplication)
            .filter(JobApplication.user_id == user_id)
            .order_by(JobApplication.updated_at.desc())
            .all()
        )
        return [
            {"id": j.id, "company": j.company, "role": j.role, "status": j.status,
             "notes": j.notes, "saved_resume_id": j.saved_resume_id,
             "created_at": j.created_at.isoformat(), "updated_at": j.updated_at.isoformat()}
            for j in rows
        ]
    finally:
        session.close()


def update_job_application_status(application_id, status):
    session = get_session()
    try:
        session.query(JobApplication).filter(JobApplication.id == application_id).update({
            "status": status,
            "updated_at": datetime.utcnow(),
        })
        session.commit()
    finally:
        session.close()


def update_job_application(application_id, company, role, notes):
    session = get_session()
    try:
        session.query(JobApplication).filter(JobApplication.id == application_id).update({
            "company": company,
            "role": role,
            "notes": notes,
            "updated_at": datetime.utcnow(),
        })
        session.commit()
    finally:
        session.close()


def delete_job_application(application_id):
    session = get_session()
    try:
        session.query(JobApplication).filter(JobApplication.id == application_id).delete()
        session.commit()
    finally:
        session.close()


# --- USAGE ANALYTICS ---

def log_event(user_id, event_name):
    session = get_session()
    try:
        session.add(UsageEvent(user_id=user_id, event_name=event_name, timestamp=datetime.utcnow()))
        session.commit()
    finally:
        session.close()


def get_event_counts():
    session = get_session()
    try:
        rows = session.query(UsageEvent.event_name, UsageEvent.id).all()
        counts = {}
        for name, _ in rows:
            counts[name] = counts.get(name, 0) + 1
        return counts
    finally:
        session.close()
