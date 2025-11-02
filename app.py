#!/usr/bin/python3

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

# App Libraries
import os
import datetime as dt
import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import tempfile

# Google Drive Libraries
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# Dashboard Libraries
from matplotlib import pyplot as plt
import pandas as pd


# My Database Functions
from functions.DatabaseFunctions import DatabaseFunctions as db
from functions.JournalFunctions import JournalFunctions as jf
from functions.SentimentFunctions import SentimentFunctions as sf
from functions.WeatherFunctions import WeatherFunctions as wth

# ---------------------------------------------------------------------
# Database Setup
# ---------------------------------------------------------------------

THIS_FOLDER = Path(__file__).parent.resolve()

## Create journal tables
absolute_path = os.path.dirname(__file__)
journal = os.path.join(absolute_path, "database", "journal.db")

# Make connection to journal database file
LOCAL_DB_PATH = db.connect_to_database(journal)


# ---------------------------------------------------------------------
# 4. Password protection
# ---------------------------------------------------------------------
password = st.text_input("Enter password", type="password")
if password != st.secrets["app_password"]:
    st.stop()

# ---------------------------------------------------------------------
# 5. Sidebar navigation
# ---------------------------------------------------------------------
st.sidebar.title("🌿 Gratitude Journal")
page = st.sidebar.radio("Go to", ["Add Entry", "View / Edit Entries", "Dashboard"])

# ---------------------------------------------------------------------
# 6. Add Entry
# ---------------------------------------------------------------------

# Required Attributes
LAT = st.secrets["LAT"]
LONG = st.secrets["LONG"]
WEATHER_API_KEY = st.secrets['WeatherAPIKey']
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
SCOPE = st.secrets["SCOPE"]

if page == "Add Entry":
    st.title("✨ Add a Gratitude Entry")
    with st.form("entry_form", clear_on_submit=True):
        text = st.text_area("What are you grateful for today? (Name at last one small thing, on thing you did for your health, and one thing you did for someone else.)", height=200)
        image = st.file_uploader("Add a picture (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Save Entry")
        if submitted and text.strip():
            image_file_id = None
            if image is not None:
                os.makedirs("temp_images", exist_ok=True)
                local_path = f"temp_images/{image.name}"
                with open(local_path, "wb") as f:
                    f.write(image.getbuffer())
                #image_file_id = upload_image_to_drive(local_path, DRIVE_FOLDER_ID)
            sentiment, mood = sf.get_sentiment(text)
            temperature, weather = wth.get_weather(LAT, LONG, WEATHER_API_KEY)
            jf.add_entry(LOCAL_DB_PATH, text, sentiment, mood, weather, temperature, image_file_id)
            st.success("Entry saved!")

# ---------------------------------------------------------------------
# 7. View / Edit Entries
# ---------------------------------------------------------------------
elif page == "View / Edit Entries":
    st.title("📔 Your Entries")
    entries = jf.get_entries(LOCAL_DB_PATH)

    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        for eid, date, text, sentiment, mood, weather, temp, song, genre, image_path in entries:
            with st.expander(f"{str(date)[:10]} — Mood: {mood}/5"):
                new_text = st.text_area("Edit text", text, key=f"text_{eid}")
                cols = st.columns(2)
                with cols[0]:
                    if st.button("💾 Save changes", key=f"save_{eid}"):
                        jf.update_entry(LOCAL_DB_PATH, eid, new_text, new_sentiment, new_mood, new_weather, new_temp, new_song, new_genre, new_image_path)
                        db.execute_sql(
                            conn,
                            """
                            UPDATE Entry
                            SET EntryText = ?, Mood = ?, DateModified = ?
                            WHERE EntryId = ?
                            """,
                            (new_text, str(new_mood), datetime.now(), eid)
                        )
                        st.success("Updated!")
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️ Delete entry", key=f"delete_{eid}"):
                        jf.delete_entry(LOCAL_DB_PATH, eid)
                        st.warning("Deleted.")
                        st.rerun()
                if image_path:
                    # Download image from Drive temporarily for display
                    try:
                        #drive_file = DRIVE.CreateFile({'id': image_path})
                        temp_image = f"temp_images/{eid}_{image_path}.jpg"
                        #drive_file.GetContentFile(temp_image)
                        st.image(temp_image, width=250)
                    except Exception:
                        st.warning("⚠️ Image could not be loaded.")

# ---------------------------------------------------------------------
# 8. Dashboard
# ---------------------------------------------------------------------
elif page == "Dashboard":
    st.title("📈 Mood Dashboard")
    df = pd.read_sql_query("SELECT * FROM Entry WHERE DateDeleted IS NULL", conn)
    if df.empty:
        st.info("No data yet to analyze.")
    else:
        df["EntryDate"] = pd.to_datetime(df["EntryDate"])
        df.sort_values("EntryDate", inplace=True)
        st.subheader("Average Mood Over Time")
        daily = df.groupby(df["EntryDate"].dt.date)["Mood"].apply(lambda x: pd.to_numeric(x, errors='coerce')).mean()
        plt.figure()
        daily.plot(marker="o")
        plt.xlabel("Date")
        plt.ylabel("Average Mood")
        plt.grid(True)
        st.pyplot(plt)
        st.subheader("Recent Entries")
        st.dataframe(df[["EntryDate", "Mood", "EntryText"]].tail(10))

# ---------------------------------------------------------------------
# 9. Upload DB back to Drive when the script ends
# ---------------------------------------------------------------------
upload_db_to_drive(file_obj)
