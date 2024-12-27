
SPOTIFY_API_URL = "https://api.spotify.com/v1"

def retrieve_api_token(client_id: str, client_secret: str) -> str:
    """Retrieves an access token for the Spotify API."""
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception("Failed to retrieve access token")
    
    return response.json()["access_token"]