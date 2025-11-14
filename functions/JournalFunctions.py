#!/usr/bin/python3
# Set of Python functions for interacting with the journal database

### Imports
from datetime import datetime
from functions.DatabaseFunctions import DatabaseFunctions as db

### Journal Functions

class JournalFunctions:
    # SQL Functions
    def get_entries(conn):
        entries = db.execute_sql_fetch_all(
        conn,
        """
        SELECT EntryId, EntryDate, EntryText, Sentiment, Mood, Weather, 
               Temperature, ImagePath
        FROM Entry
        WHERE DateDeleted IS NULL
        ORDER BY EntryDate DESC
        """
        )
        return entries

    def add_entry(conn, entry_date, text, sentiment, mood, weather, temperature, image_path=None):
        now = datetime.now()
        db.execute_sql(
            conn,
            """
            INSERT INTO Entry (EntryDate, EntryText, Sentiment, Mood, Weather, 
               Temperature, ImagePath, DateCreated, DateModified)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (entry_date, text, sentiment, mood, weather, temperature, image_path, now, now)
        )
        return True

    def update_entry(conn, eid, text, sentiment, mood, weather, temperature, image_path=None):
        now = datetime.now()
        db.execute_sql(
            conn,
            """
            UPDATE Entry
            SET EntryText = ?, Sentiment = ?, Mood = ?, Weather = ?, 
                Temperature = ?, ImagePath = ?, DateModified = ?
            WHERE EntryId = ?
            """,
            (text, sentiment, mood, weather, temperature, image_path, now, eid)
        )
        return True

    def delete_entry(conn, eid):
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
    
    def entry_exist(conn, entry_date):
        date = db.execute_sql_fetch_one(
        conn,
        """
        SELECT MAX(EntryDate)    
        FROM Entry
        WHERE EntryDate = ?
        AND DateDeleted IS NULL;
        """,
            (entry_date)
        )
        print(date[0])
        if date[0] is None:
            return False
        else:
            return True