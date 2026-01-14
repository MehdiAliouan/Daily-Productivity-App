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

## 📦 Deployment Checklist (Streamlit Community Cloud)

- [ ] **Push to GitHub**: Ensure all code (except `.env` or `secrets.toml`) is in a public/private repo.
- [ ] **requirements.txt**: Must exist in root.
- [ ] **Secrets**: go to App Settings > Secrets in Streamlit Cloud and paste your `GROQ_API_KEY`.
- [ ] **Database**: SQLite is a file-based DB. **Note**: On Streamlit Cloud, the DB will reset if the app reboots (ephemeral file system). *Recommendation: For persistent cloud data, switch `modules/database.py` to use `st.connection("postgresql")` or upload/download the DB file to S3.*
