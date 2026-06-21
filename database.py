import sqlite3
import bcrypt
from datetime import datetime
import pandas as pd

# We'll create a new database file for the SaaS version
DB_NAME = "career_platform.db"

def get_connection():
    """Helper function to get a DB connection and enforce foreign keys."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1") # Critical for relational databases
    return conn

def init_db():
    """Initializes the relational database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. USERS TABLE (Authentication)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 2. MASTER PROFILES TABLE (1-to-1 relationship with users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            phone TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            target_role TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 3. EMPLOYMENT HISTORY TABLE (1-to-Many relationship with users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            responsibilities TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 4. SKILLS TABLE (1-to-Many relationship with users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 5. AUDITS TABLE (Updated to attach to specific users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            target_role TEXT,
            score INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    # 6. PROJECTS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            description TEXT,
            link TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 7. CUSTOM SECTIONS TABLE (For Certifications, Awards, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            section_title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# --- AUTHENTICATION LOGIC ---

def create_user(email, password):
    """Securely hashes the password and creates a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate a salt and hash the password (Industry Standard Security)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Insert new user
        cursor.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                       (email, hashed.decode('utf-8'), timestamp))
        user_id = cursor.lastrowid
        
        # Automatically generate an empty profile row for this new user
        cursor.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
        
        conn.commit()
        return True # Success
    except sqlite3.IntegrityError:
        return False # Email already exists in the database
    finally:
        conn.close()

def verify_login(email, password):
    """Verifies credentials and returns the user_id if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_id, stored_hash = result
        # Check the provided password against the stored bcrypt hash
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return user_id # Login successful
            
    return None # Login failed

# --- PROFILE & DATA CRUD OPERATIONS ---

def get_profile(user_id):
    """Fetches the user's basic profile information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, phone, linkedin_url, github_url, target_role FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return profile

def update_profile(user_id, full_name, phone, linkedin, github, target_role):
    """Updates the user's basic profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profiles
        SET full_name = ?, phone = ?, linkedin_url = ?, github_url = ?, target_role = ?
        WHERE user_id = ?
    """, (full_name, phone, linkedin, github, target_role, user_id))
    conn.commit()
    conn.close()

def get_skills(user_id):
    """Fetches all skills for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, skill_name FROM skills WHERE user_id = ?", (user_id,))
    skills = cursor.fetchall()
    conn.close()
    return skills

def add_skill(user_id, skill_name):
    """Adds a new skill to the user's profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO skills (user_id, skill_name) VALUES (?, ?)", (user_id, skill_name))
    conn.commit()
    conn.close()

def get_employment(user_id):
    """Fetches employment history for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name, role_title, start_date, end_date, responsibilities FROM employment_history WHERE user_id = ?", (user_id,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def add_employment(user_id, company, role, start_date, end_date, responsibilities):
    """Adds a new job to the employment history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employment_history (user_id, company_name, role_title, start_date, end_date, responsibilities)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, company, role, start_date, end_date, responsibilities))
    conn.commit()
    conn.close()

# --- PROJECTS & CUSTOM SECTIONS CRUD ---

def get_projects(user_id):
    """Fetches all projects for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, description, link FROM projects WHERE user_id = ?", (user_id,))
    projects = cursor.fetchall()
    conn.close()
    return projects

def add_project(user_id, name, description, link):
    """Adds a new project."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (user_id, project_name, description, link) VALUES (?, ?, ?, ?)", 
                   (user_id, name, description, link))
    conn.commit()
    conn.close()

def get_custom_sections(user_id):
    """Fetches custom sections (e.g., Certifications)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, section_title, content FROM custom_sections WHERE user_id = ?", (user_id,))
    sections = cursor.fetchall()
    conn.close()
    return sections

def add_custom_section(user_id, title, content):
    """Adds a new custom section."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO custom_sections (user_id, section_title, content) VALUES (?, ?, ?)", 
                   (user_id, title, content))
    conn.commit()
    conn.close()


# --- AUDIT HISTORY CRUD ---

def save_audit(user_id, target_role, score):
    """Saves a new audit result to the user's history."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO audits (user_id, timestamp, target_role, score) VALUES (?, ?, ?, ?)", 
                   (user_id, timestamp, target_role, score))
    conn.commit()
    conn.close()

def get_history_df(user_id):
    """Fetches the user's history as a Pandas DataFrame for the progression chart."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT timestamp, target_role, score FROM audits WHERE user_id = ? ORDER BY timestamp ASC", conn, params=(user_id,))
    conn.close()
    return df

# --- UPDATE & DELETE OPERATIONS ---

def delete_employment(job_id):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM employment_history WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def update_employment_record(job_id, company, role, start, end, resp):
    conn = get_connection()
    conn.cursor().execute("""
        UPDATE employment_history
        SET company_name=?, role_title=?, start_date=?, end_date=?, responsibilities=?
        WHERE id=?
    """, (company, role, start, end, resp, job_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

def update_project_record(project_id, name, desc, link):
    conn = get_connection()
    conn.cursor().execute("UPDATE projects SET project_name=?, description=?, link=? WHERE id=?", (name, desc, link, project_id))
    conn.commit()
    conn.close()

def delete_custom_section(section_id):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM custom_sections WHERE id = ?", (section_id,))
    conn.commit()
    conn.close()

def update_custom_section_record(section_id, title, content):
    conn = get_connection()
    conn.cursor().execute("UPDATE custom_sections SET section_title=?, content=? WHERE id=?", (title, content, section_id))
    conn.commit()
    conn.close()

def delete_skill(skill_id):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    conn.commit()
    conn.close()