import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import DB_PATH # Use the centralized DB_PATH

class DatabaseManager:
    def __init__(self) -> None:
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes and returns a database connection."""
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def _init_db(self) -> None:
        """Initializes the database schema if tables do not exist and adds new columns if needed."""
        with self._get_connection() as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            
            # Tasks Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                duration INTEGER DEFAULT 30,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT,
                category TEXT DEFAULT 'Uncategorized'
            )
            """)
            
            # Add category column if it doesn't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'Uncategorized'")
            except sqlite3.OperationalError as e:
                if "duplicate column name: category" not in str(e):
                    raise # Re-raise if it's not the "duplicate column" error
            
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
    def add_task(self, name: str, priority: str = "Medium", duration: int = 30, category: str = "Uncategorized") -> str:
        """Adds a new task to the database."""
        task_id: str = str(uuid.uuid4())
        created_at: str = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (id, name, priority, duration, completed, created_at, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (task_id, name, priority, duration, False, created_at, category)
            )
        return task_id

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Retrieves all tasks from the database."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor: sqlite3.Cursor = conn.execute("SELECT * FROM tasks")
            return [dict(row) for row in cursor.fetchall()]
            
    def update_task_status(self, task_id: str, completed: bool) -> None:
        """Updates the completion status of a task."""
        with self._get_connection() as conn:
            conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
            
    def delete_task(self, task_id: str) -> None:
        """Deletes a task from the database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def update_task_details(self, task_id: str, name: str, priority: str, duration: int, category: str) -> None:
        """Updates the details of an existing task."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE tasks SET name = ?, priority = ?, duration = ?, category = ? WHERE id = ?", 
                (name, priority, duration, category, task_id)
            )

    # --- FOCUS SESSIONS ---
    def log_focus_session(self, task_id: Optional[str], duration_minutes: int) -> None:
        """Logs a focus session to the database."""
        session_id: str = str(uuid.uuid4())
        start_time: str = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO focus_sessions (id, task_id, start_time, duration_minutes) VALUES (?, ?, ?, ?)",
                (session_id, task_id, start_time, duration_minutes)
            )

    def get_focus_stats(self) -> List[Dict[str, Any]]:
        """Retrieves daily aggregated focus session statistics."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor: sqlite3.Cursor = conn.execute("""
                SELECT substr(start_time, 1, 10) as date, SUM(duration_minutes) as minutes
                FROM focus_sessions
                GROUP BY date
                ORDER BY date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
