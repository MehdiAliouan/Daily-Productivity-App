import streamlit as st
import time
from modules.database import DatabaseManager

st.set_page_config(page_title="Focus Mode", page_icon="⏱️")
db = DatabaseManager()

st.title("🔥 Focus Mode")

# --- TASK SELECTION ---
tasks = db.get_tasks()
incomplete_tasks = [t for t in tasks if not t["completed"]]

if not incomplete_tasks:
    st.info("🎉 All tasks completed! You can still run a free-style timer.")
    selected_task_id = None
else:
    # Create valid dictionary for selectbox
    task_map = {t["name"]: t["id"] for t in incomplete_tasks}
    selected_task_name = st.selectbox("Select Task to Focus On", list(task_map.keys()))
    selected_task_id = task_map[selected_task_name]

st.divider()

# --- TIMER STATE ---
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
if 'time_left' not in st.session_state:
    st.session_state.time_left = 25 * 60
if 'timer_mode' not in st.session_state:
    st.session_state.timer_mode = "Focus"
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None

# --- TIMER CONTROLS ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🍅 Pomodoro (25m)"):
        st.session_state.time_left = 25 * 60
        st.session_state.timer_mode = "Focus"
        st.session_state.timer_active = False
with col2:
    if st.button("☕ Short Break (5m)"):
        st.session_state.time_left = 5 * 60
        st.session_state.timer_mode = "Short Break"
        st.session_state.timer_active = False
with col3:
    if st.button("🧘 Long Break (15m)"):
        st.session_state.time_left = 15 * 60
        st.session_state.timer_mode = "Long Break"
        st.session_state.timer_active = False

# Display
mins, secs = divmod(st.session_state.time_left, 60)
timer_display = f"{mins:02d}:{secs:02d}"
st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{timer_display}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>{st.session_state.timer_mode}</p>", unsafe_allow_html=True)

# Actions
c1, c2 = st.columns(2)
with c1:
    label = "Pause" if st.session_state.timer_active else "Start"
    if st.button(label, use_container_width=True):
        st.session_state.timer_active = not st.session_state.timer_active
        if st.session_state.timer_active:
             st.session_state.current_task_id = selected_task_id # Lock in task
with c2:
    if st.button("Reset", use_container_width=True):
        st.session_state.timer_active = False
        st.session_state.time_left = 25 * 60

# --- TIMER LOGIC ---
if st.session_state.timer_active:
    with st.empty():
        while st.session_state.time_left > 0 and st.session_state.timer_active:
            time.sleep(1)
            st.session_state.time_left -= 1
            mins, secs = divmod(st.session_state.time_left, 60)
            st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
            
        if st.session_state.time_left == 0:
            st.session_state.timer_active = False
            st.success("Timer Complete!")
            
            # Auto-Log Session
            if st.session_state.timer_mode == "Focus":
                 duration = 25 # Simplify for MVP, ideal is to track elapsed
                 db.log_focus_session(st.session_state.current_task_id, duration)
                 st.toast(f"Logged {duration} mins to database!")
