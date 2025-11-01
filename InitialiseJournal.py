#!/usr/bin/python3

import os
from pathlib import Path
from DatabaseFunctions import DatabaseFunctions as db
import datetime as dt


THIS_FOLDER = Path(__file__).parent.resolve()

## Create journal tables
absolute_path = os.path.dirname(__file__)
journal = os.path.join(absolute_path, "database", "journal.db")

### Journal Tables

# Table to record each entry
drop_table_journal_entry = """DROP TABLE IF EXISTS Entry; """
create_table_journal_entry  = """ CREATE TABLE Entry (
                                EntryId INTEGER PRIMARY KEY AUTOINCREMENT,
                                EntryDate DATE,
                                EntryText TEXT,
                                Sentiment DECIMAL,
                                Mood TEXT,
                                Weather TEXT,
                                Temperature DECIMAL,
                                MostPlayedSong TEXT,
                                TodaysGenre TEXT,
                                ImagePath TEXT,
                                DateCreated DATETIME,
                                DateModified DATETIME,
                                DateDeleted DATETIME
                            );"""


insert_test_journal_entry = """INSERT INTO Entry (EntryDate, EntryText, Sentiment, Mood, Weather, Temperature, MostPlayedSong, TodaysGenre, ImagePath, DateCreated, DateModified, DateDeleted) VALUES
 ('2025-05-01', 'Test entry 1', 0.5, 'happy', 'sunny', 25.0, 'Song A', 'pop', 'static/images/test_image_1.png', '2025-05-01 00:00:00', '2025-05-01 00:00:00', null)
,('2025-05-02', 'Test entry 2', 0.7, 'excited', 'cloudy', 22.0, 'Song B', 'rock', 'static/images/test_image_2.png', '2025-05-02 00:00:00', '2025-05-02 00:00:00', null)
,('2025-05-03', 'Test entry 3', 0.6, 'content', 'rainy', 20.0, 'Song C', 'jazz', 'static/images/test_image_3.png', '2025-05-03 00:00:00', '2025-05-03 00:00:00', null)
,('2025-05-04', 'Test entry 4', 0.4, 'sad', 'stormy', 18.0, 'Song D', 'classical', 'static/images/test_image_4.png', '2025-05-04 00:00:00', '2025-05-04 00:00:00', null)
,('2025-05-05', 'Test entry 5', 0.8, 'joyful', 'clear', 27.0, 'Song E', 'hip-hop', 'static/images/test_image_5.png', '2025-05-05 00:00:00', '2025-05-05 00:00:00', null);"""


# Initialisation Journal Entries

# Make connection to journal database file
conn = db.connect_to_database(journal)
if conn is not None:
    # Execute required sql
    db.execute_sql(conn, drop_table_journal_entry)
    db.execute_sql(conn, create_table_journal_entry)
    db.execute_sql(conn, insert_test_journal_entry) # Only needed when loading in test data

    print("Database initialised.")
    
else:
    print("Error!")
