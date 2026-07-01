import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, ForeignKey, DateTime
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+psycopg://", 1)

# Supabase's transaction pooler (port 6543) doesn't support server-side
# prepared statements, so disable psycopg's prepared-statement cache.
_connect_args = {"prepare_threshold": None} if DATABASE_URL.startswith("postgresql+psycopg://") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    employment_history = relationship("EmploymentHistory", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    custom_sections = relationship("CustomSection", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="user", cascade="all, delete-orphan")
    saved_resumes = relationship("SavedResume", back_populates="user", cascade="all, delete-orphan")
    cover_letters = relationship("CoverLetter", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String)
    phone = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    target_role = Column(String)

    user = relationship("User", back_populates="profile")


class EmploymentHistory(Base):
    __tablename__ = "employment_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    responsibilities = Column(Text)

    user = relationship("User", back_populates="employment_history")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String)
    field_of_study = Column(String)
    start_year = Column(String)
    end_year = Column(String)
    grade = Column(String)

    user = relationship("User", back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String, nullable=False)

    user = relationship("User", back_populates="skills")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    target_role = Column(String)
    score = Column(Integer)

    user = relationship("User", back_populates="audits")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_name = Column(String, nullable=False)
    description = Column(Text)
    link = Column(String)

    user = relationship("User", back_populates="projects")


class CustomSection(Base):
    __tablename__ = "custom_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    section_title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="custom_sections")


class SavedResume(Base):
    __tablename__ = "saved_resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    job_description = Column(Text)
    template = Column(String, default="modern")
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="saved_resumes")
    job_applications = relationship("JobApplication", back_populates="saved_resume")


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    saved_resume_id = Column(Integer, ForeignKey("saved_resumes.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    company_name = Column(String)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="cover_letters")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    saved_resume_id = Column(Integer, ForeignKey("saved_resumes.id", ondelete="SET NULL"), nullable=True)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False, default="applied")
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="job_applications")
    saved_resume = relationship("SavedResume", back_populates="job_applications")


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    event_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
