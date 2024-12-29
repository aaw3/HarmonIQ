from db.models import SessionLocal

db_session = SessionLocal()

class Album:
    def fetch_album_genres(self, album_name):
        """
        Fetch genres for an album from Database.
        """
        try:
            album = session.query(Album).filter_by(name=album_name).first()
            if album:
                return album.genres
        except Exception as e:
            print(f"Error fetching genres for {album_name}: {e}")
        return []

class Artist:
    def fetch_artist_genres(self, artist_name):
        """
        Fetch genres for an artist from Database.
        """
        try:
            artist = session.query(Artist).filter_by(name=artist_name).first()
            if artist:
                return artist.genres
        except Exception as e:
            print(f"Error fetching genres for {artist_name}: {e}")
        return []
