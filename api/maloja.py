import requests
import os
from sqlalchemy.orm import Session
from db.models import Scrobble, Artist, Album, Track, SyncLog
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class MalojaScrobbleServer:
    def __init__(self, url):
        self.url = f"{url}/apis/mlj_1"

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

    def log_sync(db_session, records_synced, last_synced_date, source="maloja"):
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
        Synchronize scrobbles between the Maloja server and the local database.
        Log sync operations when new scrobbles are added.
        """
        # Get the last sync timestamp from the SyncLog table
        last_sync = db_session.query(SyncLog).filter_by(source="maloja").order_by(SyncLog.last_synced_date.desc()).first()
        since_date = last_sync.last_synced_date if last_sync else datetime(1970, 1, 1)
    
        print(f"Fetching scrobbles since: {since_date}")
        
        # Fetch new scrobbles from Maloja's API
        maloja_data = self.get_scrobbles_since(since_date.isoformat())  # Pass ISO 8601 string
    
        synced_count = 0
        most_recent_date = None
    
        for scrobble_data in maloja_data:
            try:
                # Extract timestamp
                timestamp = datetime.fromtimestamp(scrobble_data["time"])
                if not most_recent_date or timestamp > most_recent_date:
                    most_recent_date = timestamp  # Track the most recent timestamp
    
                # Extract track details
                track_name = scrobble_data["track"]["title"]
                track_length = scrobble_data["track"]["length"]
                album_name = scrobble_data["track"]["album"]["albumtitle"]
                artist_names = scrobble_data["track"]["artists"]
    
                # Fetch or create album
                album = db_session.query(Album).filter_by(name=album_name).first()
                if not album:
                    album = Album(name=album_name)
                    db_session.add(album)
    
                # Fetch or create artists
                artists = []
                for artist_name in artist_names:
                    artist = db_session.query(Artist).filter_by(name=artist_name).first()
                    if not artist:
                        artist = Artist(name=artist_name)
                        db_session.add(artist)
                    artists.append(artist)
    
                # Fetch or create track
                track = db_session.query(Track).filter_by(name=track_name, album=album).first()
                if not track:
                    track = Track(name=track_name, length=track_length, album=album)
                    track.artists = artists
                    db_session.add(track)
    
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
    
        # Log the sync if any scrobbles were added
        if synced_count > 0 and most_recent_date:
            log_sync(db_session, synced_count, most_recent_date, source="maloja")
            print(f"Logged sync: {synced_count} scrobbles synced, last scrobble at {most_recent_date}")
        else:
            print("No new scrobbles to sync.")
    