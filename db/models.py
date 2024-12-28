import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Table,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()

# Many-to-Many relationship tables
track_artists = Table(
    "track_artists",
    Base.metadata,
    Column("track_id", Integer, ForeignKey("tracks.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)

album_artists = Table(
    "album_artists",
    Base.metadata,
    Column("album_id", Integer, ForeignKey("albums.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)
# Database Models

class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)  # The source of the sync, e.g., 'maloja'
    sync_date = Column(DateTime, default=datetime.utcnow, nullable=False)  # Timestamp when the sync occurred
    last_synced_date = Column(DateTime, nullable=False)  # Timestamp of the most recent scrobble synced
    records_synced = Column(Integer, nullable=False)  # Number of scrobbles synced in this operation

# Scrobbles Table
class Scrobble(Base):
    __tablename__ = "scrobbles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    track = relationship("Track", back_populates="scrobbles")


# Artists Table
class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    genres = Column(JSON, default=[])  # List of genres (e.g., ["jazz", "ambient"])
    albums = relationship("Album", secondary=album_artists, back_populates="artists")
    tracks = relationship("Track", secondary=track_artists, back_populates="artists")

# Albums Table
class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    genres = Column(JSON, default=[])  # List of genres
    artists = relationship("Artist", secondary=album_artists, back_populates="albums")
    tracks = relationship("Track", back_populates="album")

# Tracks Table
class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    length = Column(Integer, nullable=False)  # Length of the track in seconds
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=True)
    album = relationship("Album", back_populates="tracks")
    artists = relationship("Artist", secondary=track_artists, back_populates="tracks")
    scrobbles = relationship("Scrobble", back_populates="track")


# Database connection setup using environment variables
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{urllib.parse.quote(os.getenv('POSTGRES_PASSWORD'))}@{os.getenv('POSTGRES_ADDR')}/{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)
