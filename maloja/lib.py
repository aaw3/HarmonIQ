import requests
import os
from pathlib import Path

class MalojaScrobbleServer:
    def __init__(self, url):
        self.url = Path(url) / "apis/mlj_1"

    def is_healthy(self):
        serverinfo = requests.get(f"{self.url}/serverinfo")
        if serverinfo.status_code == 200 and serverinfo["db_status"]["healthy"] == True:
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

    def sync_scrobbles(self, last_date, current_db_count):
        """
        Synchronize scrobbles by fetching only the new entries.
        :param last_date: The last known date in the local database.
        :param current_db_count: The number of scrobbles already stored locally.
        :return: List of new scrobbles.
        """
        total_scrobbles = self.get_num_scrobbles()
        if total_scrobbles <= current_db_count:
            print("No new scrobbles to fetch.")
            return []

        # Fetch new scrobbles since the last date
        print(f"Fetching scrobbles since {last_date}...")
        new_scrobbles = self.get_scrobbles_since(last_date)
        print(f"Fetched {len(new_scrobbles)} new scrobbles.")
        return new_scrobbles