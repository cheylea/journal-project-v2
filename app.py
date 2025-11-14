#!/usr/bin/python3

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

# App Libraries
import os
import streamlit as st
from pathlib import Path
from datetime import datetime

# Dashboard Libraries
from matplotlib import pyplot as plt
import pandas as pd


# My Functions
from functions.JournalFunctions import JournalFunctions as jf
from functions.SentimentFunctions import SentimentFunctions as sf
from functions.WeatherFunctions import WeatherFunctions as wth

# ---------------------------------------------------------------------
# Database Setup
# ---------------------------------------------------------------------

THIS_FOLDER = Path(__file__).parent.resolve()

from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] # anon key for read/write, or service role for secure API

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------
# 1. Password protection
# ---------------------------------------------------------------------
password = st.text_input("Enter password", type="password")
if password != st.secrets["app_password"]:
    st.stop()

# ---------------------------------------------------------------------
# 2. Sidebar navigation
# ---------------------------------------------------------------------
st.sidebar.title("🌿 Gratitude Journal")
page = st.sidebar.radio("Go to", ["Add Entry", "View / Edit Entries", "Dashboard"])

# ---------------------------------------------------------------------
# 3. Add Entry
# ---------------------------------------------------------------------

# Required Attributes
LAT = st.secrets["LAT"]
LONG = st.secrets["LONG"]
WEATHER_API_KEY = st.secrets['WeatherAPIKey']

if page == "Add Entry":
    st.title("✨ Add a Gratitude Entry")
    
    with st.form("entry_form", clear_on_submit=True):
        now = datetime.now().date()
        now_str = now.strftime("%Y-%m-%d")
        entry_exist = jf.entry_exist(supabase, (now_str,))
        if entry_exist:
            st.warning("An entry for this date already exists. Please edit it in the 'View / Edit Entries' tab.")
            st.form_submit_button("Try Again")
        else:
            text = st.text_area("What are you grateful for today? (Name at last one small thing, on thing you did for your health, and one thing you did for someone else.)", height=200)
            image = st.file_uploader("Add a picture (optional)", type=["jpg", "jpeg", "png"])
            image_path = None
            submitted = st.form_submit_button("Save Entry")
            if submitted and text.strip():
                if image is not None:
                    # Compile unique filename
                    filename, ext = os.path.splitext(image.name)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    image_name = f"{filename}_{timestamp}{ext}"

                    # Upload to Supabase Storage bucket "journal-images"
                    file_bytes = image.getvalue()
                    supabase.storage.from_("journal-images").upload(
                        image_name,
                        image.getvalue(),
                        file_options={"content-type": image.type}
                    )

                    # Get public URL so you can display and store it
                    image_path = image_name

                sentiment, mood = sf.get_sentiment(text)
                temperature, weather = wth.get_weather(LAT, LONG, WEATHER_API_KEY)
                jf.add_entry(supabase, now_str, text, sentiment, mood, weather, temperature, image_path)
                st.success("Entry saved!")

# ---------------------------------------------------------------------
# 4. View / Edit Entries
# ---------------------------------------------------------------------
elif page == "View / Edit Entries":
    st.title("📔 Your Entries")
    entries = jf.get_entries(supabase)
    
    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        for entry in entries:
            eid = entry["entryid"]
            date = entry["entrydate"]
            text = entry["entrytext"]
            sentiment = entry["sentiment"]
            mood = entry["mood"]
            weather = entry["weather"]
            temp = entry["temperature"]
            image_path = entry["imagepath"]

            with st.expander(f"{str(date)[:10]} — Mood: {mood}/5"):
                new_text = st.text_area("Edit text", text, key=f"text_{eid}")
                new_image = st.file_uploader("Change picture (optional)", type=["jpg", "jpeg", "png"], key=f"image_{eid}")
                new_image_path = None
                if new_image is not None:

                    # Compile unique filename
                    filename, ext = os.path.splitext(new_image.name)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    new_image_name = f"{filename}_{timestamp}{ext}"

                    # Upload to Supabase Storage bucket "journal-images"
                    file_bytes = new_image.getvalue()
                    supabase.storage.from_("journal-images").upload(
                        new_image_name,
                        new_image.getvalue(),
                        file_options={"content-type": new_image.type}
                    )

                    # Get public URL so you can display and store it
                    new_image_path = new_image_name

                cols = st.columns(2)
                with cols[0]:
                    if st.button("💾 Save changes", key=f"save_{eid}"):
                        new_sentiment, new_mood = sf.get_sentiment(new_text)
                        new_temperature, new_weather = wth.get_weather(LAT, LONG, WEATHER_API_KEY)
                        jf.update_entry(supabase, eid, new_text, new_sentiment, new_mood, new_weather, new_temperature, new_image_path)
                        st.success("Updated!")
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️ Delete entry", key=f"delete_{eid}"):
                        jf.delete_entry(supabase, eid)
                        st.warning("Deleted.")
                        st.rerun()
                if image_path:
                    try:
                        print(image_path)
                        signed_url = supabase.storage.from_("journal-images").create_signed_url(
                            image_path,
                            expires_in=3600  # 1 hour
                        )["signedURL"]

                        st.image(signed_url, width=300)
                    except Exception:
                        st.warning("⚠️ Image could not be loaded.")

# ---------------------------------------------------------------------
# 5. Dashboard
# ---------------------------------------------------------------------
elif page == "Dashboard":
    st.title("📈 Mood Dashboard")
    entries = jf.get_entries(supabase)

    if not entries:
        st.info("No data yet to analyze.")
    else:
        df = pd.DataFrame(entries)
        df["EntryDate"] = pd.to_datetime(df["EntryDate"])
        df.sort_values("EntryDate", inplace=True)

        # convert types
        df["Sentiment"] = pd.to_numeric(df["Sentiment"], errors="coerce")
        df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")

        # group by date
        daily_mood = df.groupby(df["EntryDate"].dt.date)["Sentiment"].mean()
        daily_temp = df.groupby(df["EntryDate"].dt.date)["Temperature"].mean()

        st.subheader("Mood + Temperature Over Time")

        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Mood (left axis)
        ax1.plot(daily_mood.index, daily_mood.values, marker="o", color="blue", label="Mood")
        ax1.set_ylabel("Average Mood", color="blue")
        ax1.set_ylim(-1, 1)  # sentiment range
        ax1.tick_params(axis='y', labelcolor="blue")
        ax1.grid(True)

        # Draw zero line for sentiment
        ax1.axhline(0, color='gray', linestyle='--', linewidth=1)

        # Temperature (right axis)
        ax2 = ax1.twinx()
        ax2.plot(daily_temp.index, daily_temp.values, marker="s", color="red", label="Temperature")
        ax2.set_ylabel("Average Temperature (°C)", color="red")
        ax2.set_ylim(-5, 35)  # UK temperature range
        ax2.tick_params(axis='y', labelcolor="red")

        # Rotate x-axis labels vertically and keep them under the plot
        plt.xticks(rotation=90)
        plt.xlabel("Date")
        plt.tight_layout()

        st.pyplot(fig)

# TODO change colours and layout
# TODO add a "home page" with some interesting stats
# TODO improve the view/edit page to have a nice timeline of entries to scroll through
# TODO set up the Steps API and ensure steps are being saved
# TODO persist password login for a session and hide it once it has it
