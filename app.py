import os
from pathlib import Path
from DatabaseFunctions import DatabaseFunctions as db
import datetime as dt
import streamlit as st
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd

THIS_FOLDER = Path(__file__).parent.resolve()

## Create journal tables
absolute_path = os.path.dirname(__file__)
journal = os.path.join(absolute_path, "database", "journal.db")

# Make connection to journal database file
conn = db.connect_to_database(journal)

# --- Sidebar navigation --------------------------------------------------
st.sidebar.title("🌿 Gratitude Journal")
page = st.sidebar.radio("Go to", ["Add Entry", "View / Edit Entries", "Dashboard"])

# --- ADD ENTRY PAGE ------------------------------------------------------
if page == "Add Entry":
    st.title("✨ Add a Gratitude Entry")
    with st.form("entry_form", clear_on_submit=True):
        text = st.text_area("What are you grateful for today?")
        mood = st.slider("Mood (1–5)", 1, 5, 3)
        image = st.file_uploader("Add a picture (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Save Entry")
        if submitted and text.strip():
            add_entry(text, mood, image)
            st.success("Entry saved!")

# --- VIEW / EDIT PAGE ----------------------------------------------------
elif page == "View / Edit Entries":
    st.title("📔 Your Entries")
    entries = db.execute_sql_fetch_all(conn, "SELECT EntryId, EntryDate, EntryText, Sentiment, Mood, Weather, Temperature, MostPlayedSong, TodaysGenre, ImagePath FROM Entry ORDER BY EntryDate DESC")

    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        for eid, date, text, mood, image_path in entries:
            with st.expander(f"{date[:10]} — Mood: {mood}/5"):
                new_text = st.text_area("Edit text", text, key=f"text_{eid}")
                new_mood = st.slider("Edit mood", 1, 5, mood, key=f"mood_{eid}")
                cols = st.columns(2)
                with cols[0]:
                    if st.button("💾 Save changes", key=f"save_{eid}"):
                        update_entry(eid, new_text, new_mood)
                        st.success("Updated!")
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️ Delete entry", key=f"delete_{eid}"):
                        delete_entry(eid)
                        st.warning("Deleted.")
                        st.rerun()
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=250)

# --- DASHBOARD PAGE ------------------------------------------------------
elif page == "Dashboard":
    st.title("📈 Mood Dashboard")
    df = pd.read_sql_query("SELECT * FROM Entry", conn)

    if df.empty:
        st.info("No data yet to analyze.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)
        st.subheader("Average Mood Over Time")
        daily = df.groupby(df["date"].dt.date)["mood"].mean()
        plt.figure()
        daily.plot(marker="o")
        plt.xlabel("Date")
        plt.ylabel("Average Mood")
        plt.grid(True)
        st.pyplot(plt)
        st.subheader("Recent Entries")
        st.dataframe(df[["date", "mood", "text"]].tail(10))