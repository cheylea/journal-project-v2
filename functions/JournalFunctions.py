#!/usr/bin/python3
# Set of Python functions for interacting with the journal database

### Imports
from datetime import datetime

### Journal Functions

class JournalFunctions:
    # Get list of journal entries
    def get_entries(supabase):
        response = (
        supabase.table("entry")
        .select("*, step!inner(steps)")
        .is_("datedeleted", None)
        .order("entrydate", desc=True)
        .execute()
        )
        return response.data
    
    # Add a new journal entry
    def add_entry(supabase, entry_date, text, sentiment, mood, weather, temperature, image_path=None):
        supabase.table("entry").insert({
            "entrydate": entry_date,
            "entrytext": text,
            "sentiment": sentiment,
            "mood": mood,
            "weather": weather,
            "temperature": temperature,
            "imagepath": image_path
        }).execute()
        return True
    

    def update_entry(supabase, eid, text, sentiment, mood, weather, temperature, image_path=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        supabase.table("entry").update({
            "entrytext": text,
            "sentiment": sentiment,
            "mood": mood,
            "weather": weather,
            "temperature": temperature,
            "imagepath": image_path,
            "datemodified": now
        }).eq("entryid", eid).execute()
        return True

    def delete_entry(supabase, eid):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        supabase.table("entry").update({
            "datemodified": now,
            "datedeleted": now
        }).eq("entryid", eid).execute()
        return True
    
    def entry_exist(supabase, entry_date):
        response = supabase.table("entry").select("entrydate").eq("entrydate", entry_date).is_("datedeleted", None).execute()
        if response.data:
            return True
        else:
            return False
        
    def add_steps(supabase, step_date, steps):
        supabase.table("step").insert({
            "stepdate": step_date,
            "steps": steps
        }).execute()

    def get_steps(supabase, date):
        response = supabase.table("step").select("steps").eq("stepdate", date).execute()
        return response.data

    def get_all_steps(supabase):
        response = supabase.table("step").select("stepdate, steps").execute()
        return response.data
    
    def upload_image(supabase, file_path, file_name):
        bucket = supabase.storage.from_("journal-images")
        with open(file_path, "rb") as f:
            bucket.upload(file_name, f)
        # Return public URL
        return bucket.get_public_url(file_name)