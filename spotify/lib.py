import requests
import os

SPOTIFY_API_URL = "https://api.spotify.com/v1"

class SpotifyAuth:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    def _get_api_token_with_credentials(self, client_id: str, client_secret: str) -> str:
        """
        Private method to retrieve an access token using provided client ID and secret.
        """
        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve access token: {response.text}")
        
        return response.json()["access_token"]

    def get_api_token(self) -> str:
        """
        Public method to retrieve an access token using environment variables.
        """
        if not self.client_id or not self.client_secret:
            raise Exception("Environment variables for SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set.")
        
        return self._get_api_token_with_credentials(self.client_id, self.client_secret)


class SpotifyAPI:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}


    class Search:
        def search(self, query, search_type="playlist", limit=20, offset=0):
            """
            Search for playlists, tracks, albums, artists, etc. on Spotify.
            """
            url = f"{SPOTIFY_API_URL}/search"
            params = {"q": query, "type": search_type, "limit": limit, "offset": offset}
            response = requests.get(url, headers=self.get_headers(), params=params)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error searching Spotify: {response.status_code} {response.text}")
                return None


    class Playlists:
        def get_playlist_tracks(self, playlist_id):
            """
            Fetch all tracks from a specific Spotify playlist.
            """
            url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks"
            tracks = []
    
            while url:
                response = requests.get(url, headers=self.get_headers())
                if response.status_code == 200:
                    data = response.json()
                    tracks.extend(data["items"])
                    url = data.get("next")  # Spotify provides the next page URL for pagination
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limited, retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    print(f"Error fetching playlist tracks: {response.status_code} {response.text}")
                    break
                
            return tracks
    
        def get_playlist_metadata(self, playlist_id):
            """
            Fetch metadata for a specific Spotify playlist.
            """
            url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}"
            response = requests.get(url, headers=self.get_headers())
    
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching playlist metadata: {response.status_code} {response.text}")
                return None
    
    