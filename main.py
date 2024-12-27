import requests
import dotenv
from spotify.lib import SpotifyAPI, SpotifyAuth
import os

def main():
    dotenv.load_dotenv()

    auth = None
    try:
        auth = SpotifyAuth()
    except Exception as e:
        print("Error while creating SpotifyAuth object")
        print(e)
        exit(1)


    api = SpotifyAPI(auth.get_api_token())

    artist_search = api.Search.search("Smashing Pumpkins", "artist", 1, 0)
    artist_search = artist_search["artists"]["items"]
    #artist_search = sorted(artist_search, key=lambda x: (x["popularity"], x["followers"]["total"]), reverse=True)
    print(artist_search)


main()