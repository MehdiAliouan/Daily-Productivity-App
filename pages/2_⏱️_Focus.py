import streamlit as st
import time
from modules.database import DatabaseManager
from config.settings import POMODORO_DURATION, SHORT_BREAK_DURATION, LONG_BREAK_DURATION
from typing import List, Dict, Any, Optional

st.set_page_config(page_title="Focus Mode", page_icon="⏱️")
db: DatabaseManager = DatabaseManager()

st.title("🔥 Focus Mode")

# --- Audio for Timer Completion ---
# Using a public domain sound from a reliable CDN.
# Ensure this URL is accessible and the sound is appropriate.
AUDIO_URL = "https://www.soundjay.com/button/button-3.wav" 
# HTML to embed and control the audio
AUDIO_HTML = f"""
<audio id="timer_beep" src="{AUDIO_URL}" type="audio/wav"></audio>
<script>
    var audio = document.getElementById('timer_beep');
    audio.volume = 0.5; // Adjust volume if needed
    function playAudio() {{
        audio.play();
    }}
</script>
"""
st.markdown(AUDIO_HTML, unsafe_allow_html=True)


# --- INITIALIZE TIMER STATE ---
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'time_left' not in st.session_state:
    st.session_state.time_left = POMODORO_DURATION * 60  # Default to Pomodoro
if 'timer_mode' not in st.session_state:
    st.session_state.timer_mode = "Focus"
if 'start_time_session' not in st.session_state:
    st.session_state.start_time_session = 0
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None
if 'session_started_at' not in st.session_state:
    st.session_state.session_started_at = None
if 'initial_duration' not in st.session_state:
    st.session_state.initial_duration = POMODORO_DURATION * 60
if 'timer_completed_flag' not in st.session_state: # Flag to prevent multiple audio plays
    st.session_state.timer_completed_flag = False

def set_timer(duration_minutes: int, mode: str):
    """Sets the timer state."""
    st.session_state.timer_running = False
    st.session_state.time_left = duration_minutes * 60
    st.session_state.initial_duration = duration_minutes * 60
    st.session_state.timer_mode = mode
    st.session_state.start_time_session = 0 # Reset actual start time
    st.session_state.session_started_at = None
    st.session_state.timer_completed_flag = False # Reset flag

# --- TASK SELECTION ---
tasks: List[Dict[str, Any]] = db.get_tasks()
incomplete_tasks: List[Dict[str, Any]] = [t for t in tasks if not t["completed"]]

selected_task_id: Optional[str] = None
if not incomplete_tasks:
    st.info("🎉 All tasks completed! You can still run a free-style timer.")
else:
    task_map: Dict[str, str] = {t["name"]: t["id"] for t in incomplete_tasks}
    selected_task_name: str = st.selectbox("Select Task to Focus On", list(task_map.keys()))
    selected_task_id = task_map[selected_task_name]

st.divider()

# --- TIMER CONTROLS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(f"🍅 Pomodoro ({POMODORO_DURATION}m)"):
        set_timer(POMODORO_DURATION, "Focus")
with col2:
    if st.button(f"☕ Short Break ({SHORT_BREAK_DURATION}m)"):
        set_timer(SHORT_BREAK_DURATION, "Short Break")
with col3:
    if st.button(f"🧘 Long Break ({LONG_BREAK_DURATION}m)"):
        set_timer(LONG_BREAK_DURATION, "Long Break")
with col4:
    if st.button("Reset"):
        set_timer(POMODORO_DURATION, "Focus")

# --- TIMER DISPLAY ---
mins, secs = divmod(st.session_state.time_left, 60)
timer_display: str = f"{mins:02d}:{secs:02d}"

st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{timer_display}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>{st.session_state.timer_mode}</p>", unsafe_allow_html=True)

# --- ACTIONS ---
c1, c2 = st.columns(2)
with c1:
    if st.button("Start/Pause", use_container_width=True):
        st.session_state.timer_running = not st.session_state.timer_running
        if st.session_state.timer_running:
            if st.session_state.start_time_session == 0:
                st.session_state.start_time_session = time.time()
                st.session_state.session_started_at = time.time()
            else:
                paused_duration = time.time() - (st.session_state.start_time_session + (st.session_state.initial_duration - st.session_state.time_left))
                st.session_state.start_time_session += paused_duration
            
            if st.session_state.current_task_id is None:
                st.session_state.current_task_id = selected_task_id
            st.session_state.timer_completed_flag = False # Reset flag on start/pause
        st.rerun()

with c2:
    if st.button("End Session & Log", use_container_width=True):
        if st.session_state.timer_mode == "Focus" and st.session_state.session_started_at is not None:
            actual_duration_seconds = min(int(time.time() - st.session_state.session_started_at), st.session_state.initial_duration)
            actual_duration_minutes = max(1, actual_duration_seconds // 60)
            
            if st.session_state.current_task_id:
                db.log_focus_session(st.session_state.current_task_id, actual_duration_minutes)
                st.toast(f"Logged {actual_duration_minutes} mins to database for task!")
            else:
                st.toast(f"Logged {actual_duration_minutes} mins to database (no task selected)!")
        
        set_timer(POMODORO_DURATION, "Focus")
        st.session_state.current_task_id = None
        st.rerun()

# --- TIMER LOGIC (Non-blocking) ---
if st.session_state.timer_running:
    if st.session_state.start_time_session == 0:
        st.session_state.start_time_session = time.time()

    elapsed_time_since_start = time.time() - st.session_state.start_time_session
    st.session_state.time_left = max(0, st.session_state.initial_duration - int(elapsed_time_since_start))

    if st.session_state.time_left > 0:
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.timer_running = False
        st.success("Timer Complete!")
        st.balloons()

        if not st.session_state.timer_completed_flag: # Play sound only once
            st.markdown("<script>playAudio();</script>", unsafe_allow_html=True)
            st.session_state.timer_completed_flag = True

        if st.session_state.timer_mode == "Focus" and st.session_state.current_task_id:
            db.log_focus_session(st.session_state.current_task_id, st.session_state.initial_duration // 60)
            st.toast(f"Logged {st.session_state.initial_duration // 60} mins to database for task!")
        elif st.session_state.timer_mode == "Focus":
            st.toast(f"Logged {st.session_state.initial_duration // 60} mins to database (no task selected)!")
        
        st.session_state.current_task_id = None


