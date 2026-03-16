from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True, nullable=False)
    provider_track_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    duration_sec = Column(Integer, default=0)
    genre = Column(String, default="unknown")
    features = Column(JSON, default={})
    stream_url = Column(String, default="")

    interactions = relationship("Interaction", back_populates="track", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    event_type = Column(String, nullable=False)  # play, like, skip, save_offline
    value = Column(Float, default=1.0)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="interactions")
    track = relationship("Track", back_populates="interactions")
