# database_init.py
import sqlite3

# Define the single database name
DB_NAME = 'app_data.db'

def initialize_all_databases():
    """
    Initializes the one master database (app_data.db)
    and creates all necessary tables.
    """
    print("Initializing master database...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- CV Generator Tables (SCHEMA CHANGED) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            profile_name TEXT NOT NULL UNIQUE,
            name TEXT, 
            contact_number TEXT, 
            email TEXT,
            location TEXT, 
            objective TEXT, 
            skills TEXT,
            photo_path TEXT 
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, title TEXT,
            description TEXT, duration TEXT, 
            FOREIGN KEY (profile_id) REFERENCES profile (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, course_name TEXT,
            year_completion TEXT, grade TEXT, institution_name TEXT,
            FOREIGN KEY (profile_id) REFERENCES profile (id) ON DELETE CASCADE
        )
    ''')
    # Removed the hardcoded 'INSERT for id=1'

    # --- To-Do List Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER NOT NULL DEFAULT 0,
            reminder_date TEXT,
            reminder_time TEXT
        )
    ''')

    # --- Notes Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Master database initialized.")