import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).parent.parent

# Data Directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# File Paths
TASKS_FILE = DATA_DIR / "tasks.json"
HABITS_FILE = DATA_DIR / "habits.json"
HISTORY_FILE = DATA_DIR / "history.json"

# App Config
APP_TITLE = "Apex Productivity"
APP_ICON = "🚀"

# Theme Colors (for Charts)
PRIMARY_COLOR = "#FF4B4B"
SECONDARY_COLOR = "#0068C9"
BACKGROUND_COLOR = "#FFFFFF"
