#!/usr/bin/python3

import os
from pathlib import Path
import sys

currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from DatabaseFunctions import DatabaseFunctions as db


THIS_FOLDER = Path(__file__).parent.resolve()

## Create journal tables
absolute_path = os.path.dirname(__file__)
journal = os.path.join(absolute_path, "journal.db")

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
                                ImagePath TEXT,
                                DateCreated DATETIME,
                                DateModified DATETIME,
                                DateDeleted DATETIME
                            );"""

# Table to store steps taken each day
drop_table_journal_steps = """DROP TABLE IF EXISTS Steps; """
create_table_journal_steps = """ CREATE TABLE Steps (
                                StepId INTEGER PRIMARY KEY AUTOINCREMENT,
                                StepDate DATE,
                                Steps INT,
                                DateCreated DATETIME,
                                DateModified DATETIME,
                                DateDeleted DATETIME
                            );"""

insert_test_journal_entry = """INSERT INTO Entry (EntryDate, EntryText, Sentiment, Mood, Weather, Temperature, ImagePath, DateCreated, DateModified, DateDeleted) VALUES
 ('2025-05-01', 'Test entry 1', 0.5, 'happy', 'sunny', 25.0, '1_test_image_1.png', '2025-05-01 00:00:00', '2025-05-01 00:00:00', null)
,('2025-05-02', 'Test entry 2', 0.7, 'excited', 'cloudy', 22.0, '2_test_image_2.png', '2025-05-02 00:00:00', '2025-05-02 00:00:00', null)
,('2025-05-03', 'Test entry 3', 0.6, 'content', 'rainy', 20.0, '3_test_image_3.png', '2025-05-03 00:00:00', '2025-05-03 00:00:00', null)
,('2025-05-04', 'Test entry 4', 0.4, 'sad', 'stormy', 18.0, '4_test_image_4.png', '2025-05-04 00:00:00', '2025-05-04 00:00:00', null)
,('2025-05-05', 'Test entry 5', 0.8, 'joyful', 'clear', 27.0, '5_test_image_5.png', '2025-05-05 00:00:00', '2025-05-05 00:00:00', null);"""

insert_test_journal_steps = """INSERT INTO Steps (StepDate, Steps, DateCreated, DateModified, DateDeleted) VALUES
 ('2025-05-01', 5000, '2025-05-01 00:00:00', '2025-05-01 00:00:00', null)
,('2025-05-02', 7500, '2025-05-02 00:00:00', '2025-05-02 00:00:00', null)
,('2025-05-03', 6000, '2025-05-03 00:00:00', '2025-05-03 00:00:00', null)
,('2025-05-04', 8000, '2025-05-04 00:00:00', '2025-05-04 00:00:00', null)
,('2025-05-05', 10000, '2025-05-05 00:00:00', '2025-05-05 00:00:00', null);"""


# Initialisation Journal Entries

# Make connection to journal database file
conn = db.connect_to_database(journal)
if conn is not None:
    # Execute required sql
    db.execute_sql(conn, drop_table_journal_entry)
    db.execute_sql(conn, create_table_journal_entry)
    #db.execute_sql(conn, insert_test_journal_entry) # Only needed when loading in test data
    db.execute_sql(conn, drop_table_journal_steps)
    db.execute_sql(conn, create_table_journal_steps)
    #db.execute_sql(conn, insert_test_journal_steps) # Only needed when loading in test data
    print("Database initialised.")
    
else:
    print("Error!")
