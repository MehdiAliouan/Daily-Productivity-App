import streamlit as st

st.set_page_config(
    page_title="Apex Productivity",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Apex Productivity Dashboard")

st.markdown("""
### Welcome to your personal command center.

Use the sidebar to navigate:
- **📝 Plan**: Manage tasks and get AI insights.
- **⏱️ Focus**: Execute tasks with a Pomodoro timer.
- **📊 Review**: Analyze your habits and progress.

#### Quick Actions
""")

col1, col2 = st.columns(2)
with col1:
    if st.button("Start 25m Focus Session"):
        st.switch_page("pages/2_⏱️_Focus.py")

with col2:
    if st.button("Review Daily Goal"):
        st.switch_page("pages/1_📝_Plan.py")

import os

if "GROQ_API_KEY" not in st.secrets and not os.getenv("GROQ_API_KEY"):
    st.info("Tip: Set your GROQ_API_KEY in `.env` or `.streamlit/secrets.toml` to enable AI features.")
else:
    st.success("AI Features Enabled 🟢")
