import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from dotenv import load_dotenv
import urllib.parse

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()

# Database Relation Tables
scrobble_artists = Table(
    "scrobble_artists",
    Base.metadata,
    Column("scrobble_id", Integer, ForeignKey("scrobbles.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)

# Database Models
class Scrobble(Base):
    """
    SQLAlchemy model for the scrobbles table in the PostgreSQL database.
    """
    __tablename__ = "scrobbles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, unique=True)
    artists = relationship(
        "Artist", secondary=scrobble_artists, back_populates="scrobbles"
    )


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    scrobbles = relationship(
        "Scrobble", secondary=scrobble_artists, back_populates="artists"
    )



# Database connection setup using environment variables
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{urllib.parse.quote(os.getenv('POSTGRES_PASSWORD'))}@{os.getenv('POSTGRES_ADDR')}/{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)
