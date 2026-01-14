import streamlit as st
import time

def render_focus_timer():
    st.header("⏱️ Focus Timer")

    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False
    if 'time_left' not in st.session_state:
        st.session_state.time_left = 25 * 60  # Default 25 mins
    if 'timer_mode' not in st.session_state:
        st.session_state.timer_mode = "Focus"

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

    # Display Timer
    mins, secs = divmod(st.session_state.time_left, 60)
    timer_display = f"{mins:02d}:{secs:02d}"
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{timer_display}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{st.session_state.timer_mode}</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Start/Pause" if not st.session_state.timer_active else "Pause"):
             st.session_state.timer_active = not st.session_state.timer_active
    with c2:
        if st.button("Reset"):
            st.session_state.timer_active = False
            st.session_state.time_left = 25 * 60

    # Timer Logic (Simple loop for demo)
    # Note: Streamlit re-runs on interaction, so a true real-time countdown needs a loop or custom component.
    # We will use a placeholder loop for visual effect if active.
    if st.session_state.timer_active:
        with st.empty():
            while st.session_state.time_left > 0 and st.session_state.timer_active:
                time.sleep(1)
                st.session_state.time_left -= 1
                mins, secs = divmod(st.session_state.time_left, 60)
                st.write(f"<h1 style='text-align: center; font-size: 80px;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                
            if st.session_state.time_left == 0:
                st.session_state.timer_active = False
                st.success("Timer Complete!")
