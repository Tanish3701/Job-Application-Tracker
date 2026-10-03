import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database file path
DB_FILE = "applications.db"

# Connect to SQLite and create table if not exists
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        date_applied TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """
)
conn.commit()

# Function to add a new application
def add_application(company, role, date_applied, status):
    cur.execute(
        "INSERT INTO applications (company, role, date_applied, status) VALUES (?, ?, ?, ?)",
        (company, role, date_applied, status),
    )
    conn.commit()

# Function to load data into DataFrame
def load_data():
    df = pd.read_sql("SELECT * FROM applications", conn)
    # Convert date string back to date for display
    if not df.empty:
        df["date_applied"] = pd.to_datetime(df["date_applied"]).dt.strftime("%b %d")
    return df

# Statistics calculation

def calculate_stats(df):
    total = len(df)
    interviews = len(df[df["status"] == "Interview"])
    offers = len(df[df["status"] == "Offer"])
    conversion_rate = (offers / total) * 100 if total > 0 else 0
    return total, interviews, offers, conversion_rate

# Streamlit UI
st.title("Job Application Tracker")

# Form to add a new application
with st.form("app_form"):
    company = st.text_input("Company")
    role = st.text_input("Role")
    date_applied = st.date_input("Date Applied", datetime.today())
    status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
    submitted = st.form_submit_button("Add Application")

    if submitted:
        add_application(
            company,
            role,
            date_applied.isoformat(),
            status,
        )
        st.success("Application added!")

# Load current data
df = load_data()

# Show stats
if not df.empty:
    total, interviews, offers, conversion_rate = calculate_stats(df)
    st.metric("Total Applications", total)
    st.metric("Interviews", interviews)
    st.metric("Offers", offers)
    st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
else:
    st.warning("No applications yet.")

# Display table of applications
st.subheader("All Applications")
st.dataframe(df)

# Status counts
if not df.empty:
    status_counts = df["status"].value_counts().reindex(["Applied", "Interview", "Offer", "Rejected"], fill_value=0)
    st.subheader("Applications by Status")
    st.bar_chart(status_counts)
