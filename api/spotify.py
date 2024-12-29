import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

class SpotifyClient:
    # Load environment variables from .env file
    def __init__(self):
        load_dotenv()

        # Configure Spotipy
        self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        ))

    def fetch_artist_genres(self, artist_name):
        """
        Fetch genres for an artist from Spotify.
        """
        try:
            # Search for the artist
            results = self.spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)
            items = results.get("artists", {}).get("items", [])
            if items:
                return items[0].get("genres", [])
        except Exception as e:
            print(f"Error fetching genres for {artist_name}: {e}")
        return []

    def fetch_track_length(self, track_name, artist_name):
        """
        Fetch the duration of a track from Spotify.
        Returns the length in seconds or None if not found.
        """
        try:
            # Search for the track on Spotify
            query = f"track:{track_name} artist:{artist_name}"
            results = self.spotify.search(q=query, type="track", limit=1)
            tracks = results.get("tracks", {}).get("items", [])
    
            if tracks:
                duration_ms = tracks[0]["duration_ms"]
                return duration_ms // 1000  # Convert milliseconds to seconds
        except Exception as e:
            print(f"Error fetching track length for '{track_name}' by '{artist_name}': {e}")
        
        return None
    
    
    