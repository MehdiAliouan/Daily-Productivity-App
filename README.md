# 🚀 Apex Productivity App

A production-grade personal productivity dashboard built with **Streamlit**, **SQLite**, and **Groq AI**.

## 🌟 Features
- **Smart Planning**: AI-assisted daily planning using Groq (Llama-3).
- **Focus Mode**: Integrated Pomodoro timer linked to specific tasks.
- **Analytics**: Real-time weekly review and habit tracking.
- **Persistence**: Robust SQLite database for data storage.

## 🛠️ Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Secrets**
    Create `.streamlit/secrets.toml`:
    ```toml
    GROQ_API_KEY = "your_groq_api_key"
    ```

3.  **Run Application**
    ```bash
    streamlit run app.py
    ```