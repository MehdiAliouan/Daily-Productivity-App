import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).parent.parent

# --- DIRECTORIES ---
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "productivity.db"

# --- APP CONFIG ---
APP_TITLE = "Apex Productivity"
APP_ICON = "🚀"

# --- TIMER SETTINGS (in minutes) ---
POMODORO_DURATION = 25
SHORT_BREAK_DURATION = 5
LONG_BREAK_DURATION = 15

# --- CAPACITY & PLANNING ---
TARGET_DAILY_HOURS = 8
TARGET_DAILY_MINUTES = TARGET_DAILY_HOURS * 60

# --- AI & MODELS ---
GROQ_MODEL = "llama-3.3-70b-versatile"

# --- THEME & UI ---
# Priority colors for badges
PRIORITY_COLORS = {
    "High": "red",
    "Medium": "orange",
    "Low": "green",
}
# Chart colors for status
STATUS_COLORS = {
    "Done": "green",
    "Todo": "orange",
}

# --- TASK CATEGORIES ---
TASK_CATEGORIES = ["Work", "Personal", "Study", "Health", "Finance", "Uncategorized"]

