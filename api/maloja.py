import requests
import os
from sqlalchemy.orm import Session
from db.models import Scrobble, Artist, Album, Track, SyncLog
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from api.spotify import SpotifyClient
import re
from tqdm import tqdm

class MalojaScrobbleServer:
    def __init__(self, url):
        self.url = f"{url}/apis/mlj_1"
        self.spotify = SpotifyClient()

    def is_healthy(self):
        response = requests.get(f"{self.url}/serverinfo")
        if response.status_code == 200 and response.json().get("db_status", {}).get("healthy", False) == True:
            return True
        
        raise Exception("Server is not healthy")

    def get_scrobbles_since_epoch(self, epoch):
        scrobbles = requests.get(f"{self.url}/scrobbles/since/{epoch}")
        return scrobbles

    
    def get_num_scrobbles(self):
        """
        Fetch the total number of scrobbles from the Maloja server.
        """
        url = f"{self.url}/numscrobbles"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("amount", 0)
        else:
            raise Exception(f"Failed to fetch numscrobbles: {response.status_code} {response.text}")


    def get_scrobbles_since(self, last_date):
        """
        Fetch all scrobbles since the given date.
        :param last_date: The last known date in 'YYYY/MM/DD' or similar format.
        :return: List of scrobbles.
        """
        params = {"from": last_date}  # Start fetching from the last known date
        response = requests.get(f"{self.url}/scrobbles", params=params)
        if response.status_code == 200:
            return response.json().get("list", [])
        raise Exception(f"Failed to fetch scrobbles: {response.status_code} {response.text}")

    def log_sync(self, db_session, records_synced, last_synced_date, source="maloja"):
        """
        Log a successful sync operation.
        """
        sync_log = SyncLog(
            source=source,
            sync_date=datetime.utcnow(),
            last_synced_date=last_synced_date,
            records_synced=records_synced,
        )
        db_session.add(sync_log)
        db_session.commit()


    def sync_scrobbles(self, db_session):
        """
        Synchronize scrobbles from Maloja and populate genres using Spotify data.
        """
        last_sync = db_session.query(SyncLog).filter_by(source="maloja").order_by(SyncLog.last_synced_date.desc()).first()
        since_date = last_sync.last_synced_date.strftime("%Y/%m/%d") if last_sync else "1970/01/01"

        print(f"Fetching scrobbles since: {since_date}")
        maloja_data = self.get_scrobbles_since(since_date)

        synced_count = 0
        most_recent_date = None

        total_scrobbles = len(maloja_data)

        with tqdm(total=total_scrobbles, desc="Syncing Scrobbles") as pbar:
            for scrobble_data in maloja_data:
                try:
                    timestamp = datetime.fromtimestamp(scrobble_data["time"])
                    if not most_recent_date or timestamp > most_recent_date:
                        most_recent_date = timestamp

                    track_name = scrobble_data["track"]["title"]
                    track_length = scrobble_data["track"]["length"]
                    album_name = scrobble_data["track"]["album"]["albumtitle"]
                    artist_names = scrobble_data["track"]["artists"]

                    if not track_length:
                        # Remove parentheses and content inside them
                        temp_track_name = re.sub(r"\(.*\)", "", track_name).strip()
                        track_length = self.spotify.fetch_track_length(temp_track_name, artist_names[0])
                        #print("new track length", track_length)

                    # Fetch or create album
                    # Fetch or create album
                    album = db_session.query(Album).filter_by(name=album_name).first()
                    if not album:
                        album = Album(name=album_name, )
                        db_session.add(album)
                        db_session.flush()  # Flush to assign an ID without committing


                    # Fetch or create artists
                    artists = []
                    for artist_name in artist_names:
                        artist = db_session.query(Artist).filter_by(name=artist_name).first()
                        if not artist:
                            artist = Artist(name=artist_name)
                            genres = self.spotify.fetch_artist_genres(artist_name)  # Fetch genres from Spotify
                            artist.genres = genres  # Update genres
                            db_session.add(artist)
                        artists.append(artist)

                        # Add artist to album if not already present
                        if artist not in album.artists:
                            album.artists.append(artist)

                    # Fetch or create track
                    track = db_session.query(Track).filter_by(name=track_name, album=album).first()
                    if not track:
                        track = Track(name=track_name, length=track_length, album=album)
                        track.artists = artists
                        album.tracks.append(track)
                        db_session.add(track)
                        db_session.flush()  # Ensure track ID is available

                    # Assign genres to albums based on artist genres
                    album_genres = set(album.genres or [])
                    for artist in artists:
                        album_genres.update(artist.genres)
                    album.genres = list(album_genres)

                    # Add scrobble
                    scrobble = db_session.query(Scrobble).filter_by(timestamp=timestamp, track=track).first()
                    if not scrobble:
                        scrobble = Scrobble(timestamp=timestamp, track=track)
                        db_session.add(scrobble)
                        synced_count += 1

                    db_session.commit()
                except IntegrityError as e:
                    db_session.rollback()
                    print(f"IntegrityError: {e}")
                except Exception as e:
                    db_session.rollback()
                    print(f"Error: {e}")
                finally:
                    pbar.update(1)

        if synced_count > 0 and most_recent_date:
            self.log_sync(db_session, synced_count, most_recent_date, source="maloja")
            print(f"Logged sync: {synced_count} scrobbles synced, last scrobble at {most_recent_date}")
        else:
            print("No new scrobbles to sync.")
