#!/usr/bin/python3
# Set of Python functions for interacting with the journal database

### Imports
from datetime import datetime
from functions.DatabaseFunctions import DatabaseFunctions as db

### Journal Functions

class JournalFunctions:
    # SQL Functions
    def get_entries(database):
        conn = db.connect_to_database(database)
        entries = db.execute_sql_fetch_all(
        conn,
        """
        SELECT EntryId, EntryDate, EntryText, Sentiment, Mood, Weather, 
               Temperature, MostPlayedSong, TodaysGenre, ImagePath
        FROM Entry
        ORDER BY EntryDate DESC
        """
        )
        return entries

    def add_entry(database, text, sentiment, mood, weather, temperature, image_file_id=None):
        conn = db.connect_to_database(database)
        now = datetime.now()
        db.execute_sql(
            conn,
            """
            INSERT INTO Entry (EntryDate, EntryText, Sentiment, Mood, Weather, 
               Temperature, ImagePath, DateCreated, DateModified)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (now.date(), text, sentiment, mood, weather, temperature, image_file_id, now, now)
        )
        return True

    def update_entry(database, eid, text, sentiment, mood, weather, temperature, image_file_id=None):
        conn = db.connect_to_database(database)
        now = datetime.now()
        db.execute_sql(
            conn,
            """
            UPDATE Entry
            SET EntryText = ?, Sentiment = ?, Mood = ?, Weather = ?, 
                Temperature = ?, ImagePath = ?, DateModified = ?
            WHERE EntryId = ?
            """,
            (text, sentiment, mood, weather, temperature, image_file_id, now, eid)
        )
        return True

    def delete_entry(database, eid):
        conn = db.connect_to_database(database)
        now = datetime.now()
        db.execute_sql(
            conn,
            """
            UPDATE Entry
            SET DateModified = ?, DateDeleted = ?
            WHERE EntryId = ?
            """,
            (now, now, eid)
        )
        return True