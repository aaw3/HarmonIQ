import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

class SpotifyClient:
    # Load environment variables from .env file
    def __init__(self):
        load_dotenv()

        # Configure Spotipy
        self.sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        ))


    def fetch_artist_genres(self, artist_name):
        """
        Fetch genres for an artist from Spotify.
        """
        try:
            # Search for the artist
            results = self.sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
            items = results.get("artists", {}).get("items", [])
            if items:
                return items[0].get("genres", [])
        except Exception as e:
            print(f"Error fetching genres for {artist_name}: {e}")
        return []
