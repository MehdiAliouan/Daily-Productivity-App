import streamlit as st
import pandas as pd
import altair as alt
from modules.database import DatabaseManager
from config.settings import STATUS_COLORS
from typing import List, Dict, Any

st.set_page_config(page_title="Review", page_icon="📊")
db: DatabaseManager = DatabaseManager()

st.title("📊 Weekly Review")

# 1. Fetch Data
focus_stats: List[Dict[str, Any]] = db.get_focus_stats()
tasks: List[Dict[str, Any]] = db.get_tasks()

# 2. Key Metrics
col1, col2, col3 = st.columns(3)
completed_count: int = sum(1 for t in tasks if t["completed"])
total_count: int = len(tasks)
completion_rate: int = int((completed_count / total_count * 100)) if total_count > 0 else 0

total_focus: int = sum(s["minutes"] for s in focus_stats)

col1.metric("Tasks Completed", f"{completed_count}/{total_count}")
col2.metric("Completion Rate", f"{completion_rate}%")
col3.metric("Total Focus Time", f"{total_focus} m")

st.divider()

# 3. Focus Chart
if not focus_stats:
    st.info("No focus sessions logged yet. Go to the Focus page and complete a timer!")
else:
    df_focus = pd.DataFrame(focus_stats)
    
    chart = alt.Chart(df_focus).mark_bar().encode(
        x=alt.X('date', title='Date'),
        y=alt.Y('minutes', title='Minutes Focused'),
        tooltip=['date', 'minutes']
    ).properties(
        title="Daily Focus Minutes"
    )
    
    st.altair_chart(chart, use_container_width=True)

# 4. Task Breakdown by Status
st.subheader("Task Status Breakdown")
if tasks:
    df_tasks = pd.DataFrame(tasks)
    status_counts = df_tasks['completed'].value_counts().reset_index()
    status_counts.columns = ['completed', 'count']
    status_counts['status'] = status_counts['completed'].apply(lambda x: 'Done' if x else 'Todo')
    
    pie_status = alt.Chart(status_counts).mark_arc().encode(
        theta=alt.Theta("count", stack=True),
        color=alt.Color("status", scale=alt.Scale(domain=list(STATUS_COLORS.keys()), range=list(STATUS_COLORS.values()))),
        tooltip=["status", "count"]
    ).properties(
        title="Tasks by Completion Status"
    )
    st.altair_chart(pie_status, use_container_width=True)

# 5. Task Breakdown by Category
st.subheader("Task Categories Breakdown")
if tasks and 'category' in df_tasks.columns:
    category_counts = df_tasks['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    pie_category = alt.Chart(category_counts).mark_arc().encode(
        theta=alt.Theta("count", stack=True),
        color=alt.Color("category"),
        tooltip=["category", "count"]
    ).properties(
        title="Tasks by Category"
    )
    st.altair_chart(pie_category, use_container_width=True)
elif tasks:
    st.info("No categories found for tasks. Please add or update tasks with categories.")
