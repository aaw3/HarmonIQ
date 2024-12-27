import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import dotenv
from db.models import engine, SessionLocal, init_db
from maloja.lib import MalojaScrobbleServer
from db.models import Base

def reset_db():
    """
    Reset the database by dropping all tables and creating them again.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def main():
    # Access database

    session = SessionLocal()
    maloja = MalojaScrobbleServer(os.getenv("MALOJA_URL"))

    # Reset db
    #reset_db()
    #exit(1)

    # Init database
    init_db()

    # Sync scrobbles
    try:
        maloja.sync_scrobbles(session)
    except Exception as e:
        print(f"Error during sync: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
