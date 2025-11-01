import os
from pathlib import Path
import datetime as dt
import streamlit as st
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile
import json
from oauth2client.service_account import ServiceAccountCredentials
from functions.DatabaseFunctions import DatabaseFunctions as db

# ---------------------------------------------------------------------
# Google Drive Authentication using Streamlit secrets
# ---------------------------------------------------------------------

def init_drive_from_service_account():
    """Authenticate with Google Drive using a service account from Streamlit secrets."""
    creds_dict = dict(st.secrets["google"])
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp:
        json.dump(creds_dict, temp)
        temp.flush()
        json_path = temp.name

    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scopes)
    gauth = GoogleAuth()
    gauth.auth_method = "service"
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)
    return drive

# ---------------------------------------------------------------------
# 1. Google Drive setup
# ---------------------------------------------------------------------
DRIVE = init_drive_from_service_account()
DRIVE_FOLDER_ID = "16f87Pusc7okePrUzeK6TYbh0MCfGvYIJ"
DB_FILENAME = "journal.db"
LOCAL_DB_PATH = Path("journal.db")

def download_db_from_drive():
    """Download the latest journal.db from Google Drive if it exists."""
    file_list = DRIVE.ListFile(
        {'q': f"'{DRIVE_FOLDER_ID}' in parents and title='{DB_FILENAME}' and trashed=false"}
    ).GetList()
    if file_list:
        file = file_list[0]
        file.GetContentFile(LOCAL_DB_PATH)
        st.sidebar.success("☁️ Downloaded journal.db from Drive")
        return file
    else:
        st.sidebar.warning("⚠️ No database found on Drive — a new one will be created.")
        return None

def upload_db_to_drive(file_obj=None):
    """Upload or update journal.db back to Google Drive."""
    if file_obj:
        file_obj.SetContentFile(LOCAL_DB_PATH)
        file_obj.Upload()
    else:
        new_file = DRIVE.CreateFile({
            "title": DB_FILENAME,
            "parents": [{"id": DRIVE_FOLDER_ID}]
        })
        new_file.SetContentFile(LOCAL_DB_PATH)
        new_file.Upload()
    st.sidebar.info("✅ Synced journal.db to Google Drive")

def upload_image_to_drive(local_image_path, folder_id):
    """Uploads a local image to Google Drive folder."""
    drive_file = DRIVE.CreateFile({
        'title': os.path.basename(local_image_path),
        'parents': [{'id': folder_id}]
    })
    drive_file.SetContentFile(local_image_path)
    drive_file.Upload()
    return drive_file['id']

# ---------------------------------------------------------------------
# 2. Download DB on startup
# ---------------------------------------------------------------------
file_obj = download_db_from_drive()

# ---------------------------------------------------------------------
# 3. Connect to the local DB
# ---------------------------------------------------------------------
conn = db.connect_to_database(str(LOCAL_DB_PATH))

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
def add_entry(text, mood, image_file_id=None):
    now = datetime.now()
    db.execute_sql(
        conn,
        """
        INSERT INTO Entry (EntryDate, EntryText, Mood, ImagePath, DateCreated, DateModified)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (now.date(), text, str(mood), image_file_id, now, now)
    )

if page == "Add Entry":
    st.title("✨ Add a Gratitude Entry")
    with st.form("entry_form", clear_on_submit=True):
        text = st.text_area("What are you grateful for today?")
        mood = st.slider("Mood (1–5)", 1, 5, 3)
        image = st.file_uploader("Add a picture (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Save Entry")
        if submitted and text.strip():
            image_file_id = None
            if image is not None:
                os.makedirs("temp_images", exist_ok=True)
                local_path = f"temp_images/{image.name}"
                with open(local_path, "wb") as f:
                    f.write(image.getbuffer())
                image_file_id = upload_image_to_drive(local_path, DRIVE_FOLDER_ID)
            add_entry(text, mood, image_file_id)
            st.success("Entry saved!")

# ---------------------------------------------------------------------
# 7. View / Edit Entries
# ---------------------------------------------------------------------
elif page == "View / Edit Entries":
    st.title("📔 Your Entries")
    entries = db.execute_sql_fetch_all(
        conn,
        """
        SELECT EntryId, EntryDate, EntryText, Sentiment, Mood, Weather, 
               Temperature, MostPlayedSong, TodaysGenre, ImagePath
        FROM Entry
        ORDER BY EntryDate DESC
        """
    )

    if not entries:
        st.info("No entries yet. Add one from the 'Add Entry' tab.")
    else:
        for eid, date, text, sentiment, mood, weather, temp, song, genre, image_path in entries:
            with st.expander(f"{str(date)[:10]} — Mood: {mood}/5"):
                new_text = st.text_area("Edit text", text, key=f"text_{eid}")
                new_mood = st.slider("Edit mood", 1, 5, int(mood), key=f"mood_{eid}")
                cols = st.columns(2)
                with cols[0]:
                    if st.button("💾 Save changes", key=f"save_{eid}"):
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
                        db.execute_sql(
                            conn,
                            """
                            UPDATE Entry
                            SET DateDeleted = ?
                            WHERE EntryId = ?
                            """,
                            (datetime.now(), eid)
                        )
                        st.warning("Deleted.")
                        st.rerun()
                if image_path:
                    # Download image from Drive temporarily for display
                    try:
                        drive_file = DRIVE.CreateFile({'id': image_path})
                        temp_image = f"temp_images/{eid}_{image_path}.jpg"
                        drive_file.GetContentFile(temp_image)
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
