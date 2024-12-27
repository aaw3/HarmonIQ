import requests
import os
from sqlalchemy.orm import Session
from db.models import Scrobble, Artist
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

    # Sync Logic
    def sync_scrobbles(self, db_session):
        """
        Synchronize scrobbles between the Maloja server and the local database.
        Log the sync if at least one scrobble is successfully synced.
        """
    
        # Fetch the last sync date
        last_sync_date = get_last_sync_date(db_session, source="maloja")
        print(f"Fetching scrobbles since: {last_sync_date or 'the beginning of time'}")
    
        # Fetch new scrobbles
        new_scrobbles = self.get_scrobbles_since(last_sync_date) if last_sync_date else self.get_scrobbles_since("1970/01/01")
    
        synced_count = 0
        most_recent_date = None
    
        for scrobble_data in new_scrobbles:
            try:
                # Extract timestamp
                time_value = scrobble_data.get("time") or scrobble_data.get("timestamp")
                if not time_value:
                    print(f"Error: Timestamp is missing for scrobble: {scrobble_data}")
                    continue
                
                timestamp = datetime.fromtimestamp(time_value)
                if not most_recent_date or timestamp > most_recent_date:
                    most_recent_date = timestamp  # Track the most recent timestamp
    
                # Extract track data
                title = scrobble_data["track"]["title"]
                artist_names = scrobble_data["track"]["artists"]
    
                # Ensure artists are unique and avoid duplicates
                artists = []
                for name in artist_names:
                    artist = db_session.query(Artist).filter_by(name=name).first()
                    if not artist:
                        artist = Artist(name=name)
                        db_session.add(artist)
                    artists.append(artist)
    
                # Create or update Scrobble
                scrobble = db_session.query(Scrobble).filter_by(title=title, timestamp=timestamp).first()
                if not scrobble:
                    scrobble = Scrobble(title=title, timestamp=timestamp, artists=artists)
                    db_session.add(scrobble)
                    synced_count += 1
    
                db_session.commit()
            except IntegrityError as e:
                db_session.rollback()
                print(f"Error during sync (IntegrityError): {e}")
            except Exception as e:
                db_session.rollback()
                print(f"Error during sync: {e}")
    
        # Log the sync if any scrobbles were synced
        if synced_count > 0 and most_recent_date:
            log_sync(db_session, synced_count, most_recent_date, source="maloja")
            print(f"Logged sync: {synced_count} scrobbles synced, last scrobble at {most_recent_date}")
        else:
            print("No new scrobbles to sync.")
        