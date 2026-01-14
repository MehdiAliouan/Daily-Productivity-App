import streamlit as st
import pandas as pd
import altair as alt
from config.settings import PRIMARY_COLOR, SECONDARY_COLOR

def render_habit_chart(habit_data):
    """
    Renders a bar chart for weekly habit completion.
    Expects data format: [{'day': 'Mon', 'completed': 5, 'total': 8}, ...]
    """
    if not habit_data:
        st.info("No habit data available yet.")
        return

    df = pd.DataFrame(habit_data)
    
    chart = alt.Chart(df).mark_bar(color=PRIMARY_COLOR).encode(
        x='day',
        y='completed',
        tooltip=['day', 'completed', 'total']
    ).properties(
        title="Weekly Habits Completed"
    )
    
    st.altair_chart(chart, use_container_width=True)

def render_focus_chart(focus_data):
    """
    Renders a line chart for focus minutes.
    Expects data format: [{'date': '2023-10-01', 'minutes': 120}, ...]
    """
    if not focus_data:
        st.info("No focus data available yet.")
        return

    df = pd.DataFrame(focus_data)
    
    chart = alt.Chart(df).mark_line(color=SECONDARY_COLOR).encode(
        x='date',
        y='minutes',
        tooltip=['date', 'minutes']
    ).properties(
        title="Daily Focus Minutes"
    )
    
    st.altair_chart(chart, use_container_width=True)
