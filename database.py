import sqlite3
import pandas as pd
from datetime import datetime

# Connect to (or create) the database file
DB_NAME = "history.db"

def init_db():
    """Creates the database table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            target_role TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_audit(target_role, score):
    """Saves a new audit result to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO audits (timestamp, target_role, score) VALUES (?, ?, ?)", 
                   (timestamp, target_role, score))
    conn.commit()
    conn.close()

def get_history_df():
    """Fetches the history and returns it as a Pandas DataFrame for easy charting."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT timestamp, target_role, score FROM audits ORDER BY timestamp ASC", conn)
    conn.close()
    return df