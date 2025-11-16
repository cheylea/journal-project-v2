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
from wordcloud import WordCloud, STOPWORDS
from matplotlib.colors import LinearSegmentedColormap

# My Functions
from functions.JournalFunctions import JournalFunctions as jf
from functions.SentimentFunctions import SentimentFunctions as sf
from functions.WeatherFunctions import WeatherFunctions as wth

# ---------------------------------------------------------------------
# Theme Setup
# ---------------------------------------------------------------------

# Custom color map for word cloud
# Theme Colours
colors = ["#E2A9C2", "#4A2E54", "#253746", "#7B3357", "#CED9E5"]
# Create a custom colormap
custom_cmap = LinearSegmentedColormap.from_list("custom_theme", colors)

st.markdown("""
<style>
/* Apply your font to all regular text elements, but NOT to icon fonts */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] * {
    font-family: 'Courier New', monospace !important;
}

/* Keep Streamlit’s Material Icons working */
[class^="material-icons"], [class*="material-icons"] {
    font-family: 'Material Icons' !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

# Set working directory
THIS_FOLDER = Path(__file__).parent.resolve()

# Database connection
from supabase import create_client, Client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] # anon key for read/write, or service role for secure API
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Weather API setup
LAT = st.secrets["LAT"]
LONG = st.secrets["LONG"]
WEATHER_API_KEY = st.secrets['WeatherAPIKey']

# ---------------------------------------------------------------------
# 1. Password protection
# ---------------------------------------------------------------------
# Initialize session state variable
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# If not yet authenticated, show password field
if not st.session_state.authenticated:
    password = st.text_input("Enter password", type="password")

    if password:
        if password == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.rerun()   # refresh to hide password field
        else:
            st.error("❌ Incorrect password!")
            st.stop()
    
    else:
        st.stop()  # wait for password input



# ---------------------------------------------------------------------
# 2. Sidebar navigation
# ---------------------------------------------------------------------
st.set_page_config(page_title="Gratitude Journal", page_icon="🌸", layout="centered")
st.sidebar.title('Where to?')
page = st.sidebar.radio("Use below to navigate", ["Home", "Add Entry", "Timeline", "Edit Entries", "Statistics"])

# ---------------------------------------------------------------------
# 3. Home Page
# ---------------------------------------------------------------------
if page == "Home":
    st.title("🌸 What are you grateful for?")
    st.markdown("*Make now always the most precious time. Now will never come again. - Jean-Luc Picard*")

    entries = jf.get_entries(supabase)
    df = pd.DataFrame(entries)
    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        #Word cloud of entries
        # Combine all text entries
        text = ' '.join(df['entrytext'].dropna().tolist())
        text = text.replace("’", "'")  # normalise curly apostrophes
        text = text.replace("'", "")   # strip all apostrophes
        # Add stop words
        custom_stopwords = STOPWORDS.union({
        'today', 'really', 'just', 'like', 'one', 'something', 'got',
        'feel', 'felt', 'time', 'day', 'much', 'make', 'made', 'wasn'
        't', 's', 'm', 've', 'll',
        "dont", "cant", "wont", "im", "youre", "hes", "shes", "its", "were", "theyre",
        "wasnt", "werent", "isnt", "arent", "havent", "hasnt", "hadnt", "id", "youd",
        "hed", "shed", "wed", "theyd", "ill", "youll", "hell", "shell", "well", "theyll",
        "ive", "youve", "weve", "theyve", "whod", "wholl", "whos", "shouldnt", "wouldnt",
        "couldnt", "mightnt", "mustnt", "neednt", "aint", "grateful", "someone else", "health",
        "still"
        })

        # WordCloud with your theme
        wordcloud = WordCloud(
            width=600, height=300,
            background_color="#F3D9E5",  # match your background if you want
            colormap=custom_cmap,
            stopwords=custom_stopwords
        ).generate(text)
        st.image(wordcloud.to_array())

        # Gallery of images
        all_images = []
        cols_per_row = 4
        # Loop to retrieve images
        for entry in entries:
            image_path = entry["imagepath"]
            if image_path:
                signed_url = supabase.storage.from_("journal-images").create_signed_url(
                    image_path,
                    expires_in=3600  # 1 hour
                )["signedURL"]
                all_images.append(signed_url)

        # Display images in a grid
        for i in range(0, len(all_images), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(all_images):
                    img_path = all_images[i + j]
                    col.image(img_path, use_container_width=True)

# ---------------------------------------------------------------------
# 4. Add an Entry
# ---------------------------------------------------------------------
elif page == "Add Entry":
    st.title("🌞 Add a Gratitude Entry")
    
    with st.form("entry_form", clear_on_submit=True):
        now = datetime.now().date()
        now_str = now.strftime("%Y-%m-%d")
        entry_exist = jf.entry_exist(supabase, (now_str,))
        if entry_exist:
            st.warning("⚠️ An entry for this date already exists. Please edit it in the 'View / Edit Entries' tab.")
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
                st.success("✅ Entry saved!")

# ---------------------------------------------------------------------
# 5. Timeline of Entries
# ---------------------------------------------------------------------
elif page == "Timeline":
    st.title("📅 Timeline")
    entries = jf.get_entries(supabase)
    
    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        for entry in entries:
            date = entry["entrydate"]
            text = entry["entrytext"]
            sentiment = entry["sentiment"]
            mood = entry["mood"]
            weather = entry["weather"]
            temp = entry["temperature"]
            image_path = entry["imagepath"]
            steps = entry["steps"]

            with st.expander(f"{str(date)[:10]}", expanded=True):
                weather_image = ""
                if "clear sky" in weather or "sun" in weather:
                    weather_image = "☀️"
                elif "thunder" in weather:
                    weather_image = "🌩️"
                elif "rain" in weather:
                    weather_image = "🌧️"
                elif "drizzle" in weather:
                    weather_image = "🌦️"
                elif "snow" in weather:
                    weather_image = "❄️"
                elif "clouds" in weather and "overcast" not in weather:
                    weather_image = "⛅"
                else:
                    weather_image = "☁️"

                st.write(f"**Mood:** {mood} ({sentiment}) ● **Weather:** {weather_image} ({temp}°C) ● **Steps**: {steps}")

                if image_path:
                    col_text, col_image = st.columns([4, 2])
                    with col_text:
                        st.write(f"{text}")
                    
                    with col_image:
                        try:
                            signed_url = supabase.storage.from_("journal-images").create_signed_url(
                                image_path,
                                expires_in=3600  # 1 hour
                            )["signedURL"]
    
                            st.image(signed_url, width=300)
                        except Exception:
                            st.warning("⚠️ Image could not be loaded.")
                else:
                    st.write(f"**Entry Text:** {text}")

# ---------------------------------------------------------------------
# 6. Edit Entries
# ---------------------------------------------------------------------
elif page == "Edit Entries":
    st.title("📔 Edit Entries")
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
            steps = entry["steps"]

            with st.expander(f"{str(date)[:10]}", expanded=False):
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
                        st.success("✅ Updated!")
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️ Delete entry", key=f"delete_{eid}"):
                        jf.delete_entry(supabase, eid)
                        st.warning("⚠️ Deleted.")
                        st.rerun()
                if image_path:
                    try:
                        signed_url = supabase.storage.from_("journal-images").create_signed_url(
                            image_path,
                            expires_in=3600  # 1 hour
                        )["signedURL"]

                        st.image(signed_url, width=300)
                    except Exception:
                        st.warning("⚠️ Image could not be loaded.")

# ---------------------------------------------------------------------
# 7. Statistics Dashboard
# ---------------------------------------------------------------------
elif page == "Statistics":
    st.title("📈 Statistics")
    entries = jf.get_entries(supabase)

    if not entries:
        st.info("No data yet to analyze.")
    else:
        df = pd.DataFrame(entries)
        df["entrydate"] = pd.to_datetime(df["entrydate"])
        df.sort_values("entrydate", inplace=True)

        # convert types
        df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
        df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
        df["steps"] = pd.to_numeric(df["steps"], errors="coerce")

        # group by date
        daily_mood = df.groupby(df["entrydate"].dt.date)["sentiment"].mean()
        daily_temp = df.groupby(df["entrydate"].dt.date)["temperature"].mean()
        daily_steps = df.groupby(df["entrydate"].dt.date)["steps"].mean()

        # Normalise for combined graph
        def Normalise(series):
            return (series - series.min()) / (series.max() - series.min())

        mood_norm = Normalise(daily_mood)
        temp_norm = Normalise(daily_temp)
        steps_norm = Normalise(daily_steps)

        # -----------------------
        # Combined Normalised graph
        # -----------------------
        st.subheader("Mood, Temperature, and Steps Over Time (Normalised)")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(mood_norm.index, mood_norm.values, marker="o", color="#4A2E54", label="Mood")
        ax.plot(temp_norm.index, temp_norm.values, marker="o", color="#7B3357", label="Temperature")
        ax.plot(steps_norm.index, steps_norm.values, marker="o", color="#E2A9C2", label="Steps")
        ax.set_ylabel("Normalised Value (0-1)")
        ax.set_xlabel("Date")
        ax.set_title("Trends Over Time")
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

        # -----------------------
        # Individual graphs
        # -----------------------
        st.subheader("Mood Over Time")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(daily_mood.index, daily_mood.values, marker="o", color="#4A2E54")
        ax.set_ylabel("Average Mood")
        ax.set_xlabel("Date")
        ax.set_ylim(-1, 1)
        ax.grid(True)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

        st.subheader("Temperature Over Time")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(daily_temp.index, daily_temp.values, marker="o", color="#7B3357")
        ax.set_ylabel("Average Temperature (°C)")
        ax.set_xlabel("Date")
        ax.set_ylim(daily_temp.min() - 5, daily_temp.max() + 5)
        ax.grid(True)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

        st.subheader("Steps Over Time")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(daily_steps.index, daily_steps.values, marker="o", color="#E2A9C2")
        ax.set_ylabel("Average Steps")
        ax.set_xlabel("Date")
        ax.set_ylim(daily_steps.min() - 500, daily_steps.max() + 500)
        ax.grid(True)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)


# TODO improve graphs
