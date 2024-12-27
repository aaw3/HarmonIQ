import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import dotenv

def main():
    dotenv.load_dotenv()

    # Set your Spotify API credentials
    # get client id with dotenv
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))

    # Search for an artist
    result = sp.search(q="Massive Attack", type="artist", limit=1)
    artist = result["artists"]["items"][0]
    print(f"Artist: {artist['name']}, Followers: {artist['followers']['total']}, Popularity: {artist['popularity']}")


main()