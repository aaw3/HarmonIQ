import requests
import dotenv
from spotify import lib as spotify_lib

def main():
    dotenv.load_dotenv()

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    token = spotify_lib.get_api_token(client_id, client_secret)
    print(token)

main()