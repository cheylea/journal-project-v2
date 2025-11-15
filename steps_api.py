from fastapi import FastAPI
from pydantic import BaseModel
from functions.JournalFunctions import JournalFunctions as jf
import uvicorn
import os
from supabase import create_client, Client

# Database connection
SUPABASE_URL = os.environ.get("SUPABASE_URL") # railway
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # railway
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class StepsPayload(BaseModel):
    date: str
    steps: int

@app.post("/add_steps")
def receive_steps(payload: StepsPayload):
    jf.add_steps(supabase, payload.date, payload.steps)
    return {"status": "ok", "message": "Steps recorded"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
