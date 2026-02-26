import streamlit as st
import time
from modules.database import DatabaseManager
from modules.execution import ExecutionEngine
from modules.groq_client import GroqClient
from config.settings import TARGET_DAILY_MINUTES, TARGET_DAILY_HOURS, PRIORITY_COLORS, TASK_CATEGORIES
from typing import List, Dict, Any

st.set_page_config(page_title="Plan Your Day", page_icon="📝", layout="wide")

# --- Initialization ---
db: DatabaseManager = DatabaseManager()
execution_engine: ExecutionEngine = ExecutionEngine()
groq_client: GroqClient = GroqClient()

st.title("📝 Daily Planning")

# --- SIDEBAR: ADD TASK ---
with st.sidebar:
    st.header("Add New Task")
    with st.form("add_task_form", clear_on_submit=True):
        new_task_name: str = st.text_input("Task Name", placeholder="e.g. Deep Work on Project X")
        new_task_priority: str = st.selectbox("Priority", list(PRIORITY_COLORS.keys()), index=1)
        new_task_duration: int = st.number_input("Duration (mins)", min_value=5, value=30, step=5)
        new_task_category: str = st.selectbox("Category", TASK_CATEGORIES, index=TASK_CATEGORIES.index("Uncategorized"))
        
        submitted: bool = st.form_submit_button("Add Task")
        if submitted and new_task_name:
            db.add_task(new_task_name, new_task_priority, new_task_duration, new_task_category)
            st.success("Task Added!")
            time.sleep(0.5)
            st.rerun()

# --- MAIN CONTENT ---

# 1. Fetch & Sort
tasks: List[Dict[str, Any]] = db.get_tasks()
sorted_tasks: List[Dict[str, Any]] = execution_engine.prioritize_tasks(tasks)

# 2. Capacity Indicator
total_minutes: int = execution_engine.calculate_capacity(tasks)
encoded_hours: float = total_minutes / 60
capacity_percentage: float = min(total_minutes / TARGET_DAILY_MINUTES, 1.0)

col_cap1, col_cap2 = st.columns([3, 1])
with col_cap1:
    st.progress(capacity_percentage, text=f"Daily Load: {int(encoded_hours)}h {total_minutes%60}m / {TARGET_DAILY_HOURS}h Target")
with col_cap2:
    if total_minutes > TARGET_DAILY_MINUTES:
        st.warning("⚠️ Over Capacity!", icon="🔥")
    else:
        st.success("✅ Good Balance", icon="🧘")

st.divider()

# 3. Task List (Editable)
st.subheader(f"Today's Tasks ({len(tasks)})")

if not sorted_tasks:
    st.info("No tasks yet. Use the sidebar to add some!")

for task in sorted_tasks:
    t_id: str = task["id"]
    
    if f"edit_mode_{t_id}" not in st.session_state:
        st.session_state[f"edit_mode_{t_id}"] = False

    container = st.container(border=True)
    with container:
        if not st.session_state[f"edit_mode_{t_id}"]:
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 1.5, 1, 1, 1]) # Added one more column for category
            
            with c1:
                is_done: bool = bool(task["completed"])
                new_status: bool = st.checkbox("", value=is_done, key=f"check_{t_id}")
                if new_status != is_done:
                    db.update_task_status(t_id, new_status)
                    st.rerun()

            with c2:
                title_style = "text-decoration: line-through; color: grey;" if task["completed"] else "font-weight: bold;"
                st.markdown(f"<span style='{title_style}'>{task['name']}</span>", unsafe_allow_html=True)
            
            with c3:
                color = PRIORITY_COLORS.get(task['priority'], 'grey')
                st.markdown(f":{color}[{task['priority']}]")

            with c4:
                st.caption(f"⏱️ {task['duration']}m")

            with c5: # Display Category
                st.caption(f"📂 {task.get('category', 'Uncategorized')}") # Use .get for backward compatibility

            with c6:
                b1, b2 = st.columns(2)
                if b1.button("✏️", key=f"btn_edit_{t_id}", help="Edit Task"):
                    st.session_state[f"edit_mode_{t_id}"] = True
                    st.rerun()
                if b2.button("🗑️", key=f"btn_del_{t_id}", help="Delete Task"):
                    db.delete_task(t_id)
                    st.rerun()
        
        else: # Edit View
            with st.form(f"edit_form_{t_id}"):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1]) # Added one more column for category
                new_name = c1.text_input("Name", value=task["name"])
                new_prio = c2.selectbox("Priority", list(PRIORITY_COLORS.keys()), index=list(PRIORITY_COLORS.keys()).index(task["priority"]))
                new_dur = c3.number_input("Mins", value=task["duration"], step=5)
                new_cat = c4.selectbox("Category", TASK_CATEGORIES, index=TASK_CATEGORIES.index(task.get("category", "Uncategorized"))) # Use .get
                
                if st.form_submit_button("💾 Save"):
                    db.update_task_details(t_id, new_name, new_prio, new_dur, new_cat)
                    st.session_state[f"edit_mode_{t_id}"] = False
                    st.rerun()
            
            if st.button("Cancel", key=f"cancel_{t_id}"):
                st.session_state[f"edit_mode_{t_id}"] = False
                st.rerun()

# 4. AI Planning
st.divider()
st.subheader("🤖 AI Planner Assistant")
if st.button("🔮 Generate Today's Execution Plan"):
    with st.spinner("Consulting the architect..."):
        todo_tasks = [t for t in sorted_tasks if not t["completed"]]
        if not todo_tasks:
            st.info("No pending tasks to plan!")
        else:
            context = "\n".join([f"- {t['name']} ({t['priority']}, {t['duration']}m, Category: {t.get('category', 'Uncategorized')})" for t in todo_tasks])
            plan = groq_client.get_completion("daily_planning", user_context=context, target_daily_hours=TARGET_DAILY_HOURS)
            st.markdown(plan)
