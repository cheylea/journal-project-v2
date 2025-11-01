#!/usr/bin/python3
# Set of functions to access song data from Spotify API

### Imports
from datetime import datetime, timezone
import token
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
from dotenv import load_dotenv # for variables
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE')


### Song Functions

class SongFunctions:
    def get_song_and_genre(client_id, client_secret, redirect_uri, scope):
        sp_oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=".spotifycache"  # optional
        )

        sp = spotipy.Spotify(auth_manager=sp_oauth)
        recent_tracks = sp.current_user_recently_played(limit=50)

        today = datetime.now(timezone.utc).date()

        # Only songs from today
        today_tracks = [
            item for item in recent_tracks['items']
            if datetime.fromisoformat(item['played_at'].replace('Z', '+00:00')).date() == today
        ]

        if not today_tracks:
            return None, "No songs played today"

        track_names = [item['track']['name'] for item in today_tracks]
        most_common_track_name, _ = Counter(track_names).most_common(1)[0]

        for item in today_tracks:
            if item['track']['name'] == most_common_track_name:
                track = item['track']
                artist_id = track['artists'][0]['id']
                break

        artist = sp.artist(artist_id)
        genres = artist.get('genres', [])

        return most_common_track_name, genres[0] if genres else "Unknown"