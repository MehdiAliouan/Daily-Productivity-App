
import streamlit as st
import time

def focus_timer():
    st.markdown("### ⏱️ Focus Timer")

    # --- Timer Options ---
    timer_mode = st.radio("Select Timer Mode", ["Pomodoro (25 min)", "Short Break (5 min)", "Long Break (15 min)", "Custom"], horizontal=True)

    if timer_mode == "Custom":
        custom_duration = st.number_input("Enter duration in minutes:", min_value=1, value=10)
        duration_seconds = custom_duration * 60
    elif timer_mode == "Pomodoro (25 min)":
        duration_seconds = 25 * 60
    elif timer_mode == "Short Break (5 min)":
        duration_seconds = 5 * 60
    else: # Long Break
        duration_seconds = 15 * 60

    # --- Timer Controls ---
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("Start Timer")
    with col2:
        stop_button = st.button("Stop Timer")

    # --- Timer Display ---
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
        st.session_state.start_time = 0

    if start_button:
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()

    if stop_button:
        st.session_state.timer_running = False

    if st.session_state.timer_running:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(0, duration_seconds - elapsed_time)

        if remaining_time == 0:
            st.session_state.timer_running = False
            st.success("Time's up! 🎉")
            st.balloons()
        else:
            mins, secs = divmod(remaining_time, 60)
            timer_display = f"{int(mins):02d}:{int(secs):02d}"
            st.markdown(f"<h1 style='text-align: center; color: green;'>{timer_display}</h1>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
