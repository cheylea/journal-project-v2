#!/usr/bin/python3
# Set of Python functions for interacting with the journal database.
# These Journal Functions interact with the Supabase database to manage journal entries.
# https://supabase.com/

# Imports
from datetime import datetime

class JournalFunctions:
    @staticmethod
    # Get list of journal entries
    def get_entries(supabase):
        """ Get list of journal entries with associated steps for that day.

        Args:
            supabase: Supabase client instance

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        # Fetch all entries
        entries = (
            supabase.table("entry")
            .select("*")
            .is_("datedeleted", None)
            .order("entrydate", desc=True)
            .execute()
            .data
        )

        # Fetch all steps
        steps = supabase.table("step").select("stepdate, steps").execute().data
        steps_map = {s["stepdate"]: s["steps"] for s in steps}

        # Join manually
        for e in entries:
            e["steps"] = steps_map.get(e["entrydate"])

        return entries
    
    # Add a new journal entry
    def add_entry(supabase, entry_date, text, sentiment, mood, weather, temperature, topic, image_path=None ):
        """ Add a new journal entry to the database.

        Args:
            supabase: Supabase client instance
            entry_date: Date of the journal entry (YYYY-MM-DD)
            text: Text content of the journal entry
            sentiment: Sentiment analysis result (between -1 and 1)
            mood: Mood rating (detected mood)
            weather: Weather description
            temperature: Temperature value
            image_path: Optional path to an associated image
            topic: Identified topic for the entry

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            """
        supabase.table("entry").insert({
            "entrydate": entry_date,
            "entrytext": text,
            "sentiment": sentiment,
            "mood": mood,
            "weather": weather,
            "temperature": temperature,
            "imagepath": image_path,
            "topic": topic
        }).execute()
        return True
    

    def update_entry(supabase, eid, text, sentiment, mood, weather, temperature, topic, image_path=None):
        """ Update an existing journal entry in the database.

        Args:
            supabase: Supabase client instance
            eid: Entry ID of the journal entry to update
            text: Updated text content of the journal entry
            sentiment: Updated sentiment analysis result (between -1 and 1)
            mood: Updated mood rating (detected mood)
            weather: Updated weather description
            temperature: Updated temperature value
            image_path: Optional updated path to an associated image
            topic: Identified topic for the entry

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        supabase.table("entry").update({
            "entrytext": text,
            "sentiment": sentiment,
            "mood": mood,
            "weather": weather,
            "temperature": temperature,
            "imagepath": image_path,
            "topic": topic,
            "datemodified": now
        }).eq("entryid", eid).execute()
        return True

    def delete_entry(supabase, eid):
        """ Soft delete a journal entry by setting datedeleted.

        Args:
            supabase: Supabase client instance
            eid: Entry ID of the journal entry to delete
            
            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        supabase.table("entry").update({
            "datemodified": now,
            "datedeleted": now
        }).eq("entryid", eid).execute()
        return True
    
    def entry_exist(supabase, entry_date):
        """ Check if a journal entry exists for a given date.

        Args:
            supabase: Supabase client instance
            entry_date: Date to check for existing journal entry (YYYY-MM-DD)

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        response = supabase.table("entry").select("entrydate").eq("entrydate", entry_date).is_("datedeleted", None).execute()
        if response.data:
            return True
        else:
            return False
        
    def add_steps(supabase, step_date, steps):
        """ Add step count data for a specific date.

        Args:
            supabase: Supabase client instance
            step_date: Date for the step count data (YYYY-MM-DD)
            steps: Number of steps

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        supabase.table("step").insert({
            "stepdate": step_date,
            "steps": steps
        }).execute()

    def get_steps(supabase, date):
        """ Get step count for a specific date.

        Args:
            supabase: Supabase client instance
            date: Date to retrieve step count for (YYYY-MM-DD)

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        response = supabase.table("step").select("steps").eq("stepdate", date).execute()
        return response.data

    def get_all_steps(supabase):
        """ Get all step count data.

        Args:
            supabase: Supabase client instance

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        response = supabase.table("step").select("stepdate, steps").execute()
        return response.data
    
    def upload_image(supabase, file_path, file_name):
        """ Upload an image to Supabase storage.

        Args:
            supabase: Supabase client instance
            file_path: Local path to the image file
            file_name: Desired name for the uploaded file in storage

            To create a supabase client instance
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)"""
        bucket = supabase.storage.from_("journal-images")
        with open(file_path, "rb") as f:
            bucket.upload(file_name, f)
        # Return public URL
        return bucket.get_public_url(file_name)
