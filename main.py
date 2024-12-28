import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import dotenv
from db.models import engine, SessionLocal, init_db
from maloja.lib import MalojaScrobbleServer
from db.models import Base
from sqlalchemy import Table, MetaData

def reset_db():
    """
    Reset the database by dropping all tables and creating them again.
    """

    # Reflect metadata and drop dependent tables first
    #meta = MetaData()
    #meta.reflect(bind=engine)
    #
    ## Drop association table first
    #scrobble_artists = Table('scrobble_artists', meta, autoload_with=engine)
    #scrobble_artists.drop(bind=engine)
    #
    ## Drop artists table
    #artists = Table('artists', meta, autoload_with=engine)
    #artists.drop(bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    exit(1)

def main():
    # Access database

    session = SessionLocal()
    maloja = MalojaScrobbleServer(os.getenv("MALOJA_URL"))

    # Reset db
    #reset_db()

    # Init database
    #init_db()

    # Sync scrobbles
    try:
        maloja.sync_scrobbles(session)
    except Exception as e:
        print(f"Error during sync: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
