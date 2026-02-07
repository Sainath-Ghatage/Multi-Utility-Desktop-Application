# todo_database_funcs.py
import sqlite3

# Define the single database name
DB_NAME = 'app_data.db'

# --- init_db() function removed ---
# It is now handled by database_init.py

def add_task(title, description, reminder_date, reminder_time):
    """Adds a new task to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, reminder_date, reminder_time) VALUES (?, ?, ?, ?)",
        (title, description, reminder_date, reminder_time)
    )
    conn.commit()
    conn.close()

def get_all_tasks():
    """Retrieves all tasks from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task(task_id, title, description, reminder_date, reminder_time):
    """Updates an existing task."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title=?, description=?, reminder_date=?, reminder_time=? WHERE id=?",
        (title, description, reminder_date, reminder_time, task_id)
    )
    conn.commit()
    conn.close()

def update_task_status(task_id, done):
    """Updates the 'done' status of a task."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done=? WHERE id=?", (done, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Deletes a task from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()