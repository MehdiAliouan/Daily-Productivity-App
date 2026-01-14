import streamlit as st
import time
from modules.database import DatabaseManager
from modules.execution import ExecutionEngine
from modules.groq_client import GroqClient

st.set_page_config(page_title="Plan Your Day", page_icon="📝", layout="wide")

db = DatabaseManager()
execution_engine = ExecutionEngine()
groq_client = GroqClient()

st.title("📝 Daily Planning")

# --- SIDEBAR: ADD TASK ---
with st.sidebar:
    st.header("Add New Task")
    with st.form("add_task_form", clear_on_submit=True):
        new_task_name = st.text_input("Tas Name", placeholder="e.g. Deep Work on Project X")
        new_task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        new_task_duration = st.number_input("Duration (mins)", min_value=5, value=30, step=5)
        
        submitted = st.form_submit_button("Add Task")
        if submitted and new_task_name:
            db.add_task(new_task_name, new_task_priority, new_task_duration)
            st.success("Task Added!")
            time.sleep(0.5)
            st.rerun()

# --- MAIN CONTENT ---

# 1. Fetch & Sort
tasks = db.get_tasks()
sorted_tasks = execution_engine.prioritize_tasks(tasks)

# 2. Capacity Indicator
total_minutes = execution_engine.calculate_capacity(tasks)
encoded_hours = total_minutes / 60
capacity_percentage = min(total_minutes / 480, 1.0) # 480 mins = 8 hours

col_cap1, col_cap2 = st.columns([3, 1])
with col_cap1:
    st.progress(capacity_percentage, text=f"Daily Load: {int(encoded_hours)}h {total_minutes%60}m / 8h Target")
with col_cap2:
    if total_minutes > 480:
        st.warning("⚠️ Over Capacity!", icon="🔥")
    else:
        st.success("✅ Good Balance", icon="🧘")

st.divider()

# 3. Task List (Editable)
st.subheader(f"Today's Tasks ({len(tasks)})")

if not sorted_tasks:
    st.info("No tasks yet. Use the sidebar to add some!")

for task in sorted_tasks:
    # Unique key for every widget based on Task ID
    t_id = task["id"]
    
    # Inline Edit Mode Toggle
    if f"edit_mode_{t_id}" not in st.session_state:
        st.session_state[f"edit_mode_{t_id}"] = False

    container = st.container(border=True)
    with container:
        # Standard View
        if not st.session_state[f"edit_mode_{t_id}"]:
            c1, c2, c3, c4, c5 = st.columns([0.5, 4, 1.5, 1, 1])
            
            with c1:
                # Completion Checkbox
                is_done = task["completed"]
                if st.checkbox("", value=bool(is_done), key=f"check_{t_id}"):
                    if not is_done:
                        db.update_task_status(t_id, True)
                        st.rerun()
                elif not st.checkbox("", value=bool(is_done), key=f"uncheck_{t_id}"):
                     if is_done:
                        db.update_task_status(t_id, False)
                        st.rerun()

            with c2:
                title_style = "text-decoration: line-through; color: grey;" if task["completed"] else "font-weight: bold;"
                st.markdown(f"<span style='{title_style}'>{task['name']}</span>", unsafe_allow_html=True)
            
            with c3:
                # Priority Badge
                colors = {"High": "red", "Medium": "orange", "Low": "green"}
                st.markdown(f":{colors[task['priority']]}[{task['priority']}]")

            with c4:
                st.caption(f"⏱️ {task['duration']}m")

            with c5:
                # Action Buttons
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✏️", key=f"btn_edit_{t_id}", help="Edit Task"):
                        st.session_state[f"edit_mode_{t_id}"] = True
                        st.rerun()
                with b2:
                    if st.button("🗑️", key=f"btn_del_{t_id}", help="Delete Task"):
                        db.delete_task(t_id)
                        st.rerun()
        
        # Edit View
        else:
            with st.form(f"edit_form_{t_id}"):
                c1, c2, c3 = st.columns([3, 1, 1])
                new_name = c1.text_input("Name", value=task["name"])
                new_prio = c2.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task["priority"]))
                new_dur = c3.number_input("Mins", value=task["duration"], step=5)
                
                save_col, cancel_col = st.columns([1, 1])
                if save_col.form_submit_button("💾 Save"):
                    db.update_task_details(t_id, new_name, new_prio, new_dur)
                    st.session_state[f"edit_mode_{t_id}"] = False
                    st.rerun()
                
                # Note: Cancel in forms is tricky, simplified by just re-rendering on next run or separate button outside form.
                # For cleaner UI, we just rely on Save or manual toggle back if we added a cancel button outside.
            
            if st.button("Cancel", key=f"cancel_{t_id}"):
                st.session_state[f"edit_mode_{t_id}"] = False
                st.rerun()


# 4. AI Planning
st.divider()
st.subheader("🤖 AI Planner Assistant")
if st.button("🔮 Generate Today's Execution Plan"):
    with st.spinner("Consulting the architect..."):
        # Filter only Todo items
        todo_tasks = [t for t in sorted_tasks if not t["completed"]]
        if not todo_tasks:
            st.info("No pending tasks to plan!")
        else:
            context = "\n".join([f"- {t['name']} ({t['priority']}, {t['duration']}m)" for t in todo_tasks])
            plan = groq_client.get_completion("daily_planning", user_context=context)
            st.markdown(plan)
