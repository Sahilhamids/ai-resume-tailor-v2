import sqlite3

def init_db():
    # 1. Connect to SQLite (this automatically creates a file named 'resume_app.db' if it doesn't exist)
    conn = sqlite3.connect('resume_app.db')
    cursor = conn.cursor()

    # 2. Write the SQL query to create a table for our generated resumes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description TEXT,
            filename TEXT,
            ai_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Save the changes and close the connection
    conn.commit()
    conn.close()
    
    print("Database and table successfully created!")

if __name__ == "__main__":
    init_db()