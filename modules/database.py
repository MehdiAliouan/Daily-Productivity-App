import sqlite3
import uuid
from datetime import datetime, date
from config.settings import DATA_DIR
import os

DB_PATH = os.path.join(DATA_DIR, "productivity.db")

class DatabaseManager:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                duration INTEGER DEFAULT 30,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT
            )
            """)
            
            # Focus Sessions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                start_time TEXT,
                duration_minutes INTEGER,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
            """)
            conn.commit()

    # --- TASKS ---
    def add_task(self, name, priority="Medium", duration=30):
        task_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (id, name, priority, duration, completed, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (task_id, name, priority, duration, False, created_at)
            )
        return task_id

    def get_tasks(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks")
            return [dict(row) for row in cursor.fetchall()]
            
    def update_task_status(self, task_id, completed):
        with self._get_connection() as conn:
            conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
            
    def delete_task(self, task_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def update_task_details(self, task_id, name, priority, duration):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE tasks SET name = ?, priority = ?, duration = ? WHERE id = ?", 
                (name, priority, duration, task_id)
            )

    # --- FOCUS SESSIONS ---
    def log_focus_session(self, task_id, duration_minutes):
        session_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO focus_sessions (id, task_id, start_time, duration_minutes) VALUES (?, ?, ?, ?)",
                (session_id, task_id, start_time, duration_minutes)
            )

    def get_focus_stats(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            # Simple daily aggregation
            cursor = conn.execute("""
                SELECT substr(start_time, 1, 10) as date, SUM(duration_minutes) as minutes
                FROM focus_sessions
                GROUP BY date
                ORDER BY date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
