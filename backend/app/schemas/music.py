from typing import Literal

from pydantic import BaseModel, Field


class UnifiedTrack(BaseModel):
    provider: Literal["spotify", "soundcloud", "ytmusic"]
    provider_track_id: str
    title: str
    artist: str
    duration_sec: int = 0
    genre: str = "unknown"
    stream_url: str = ""


class SearchResponse(BaseModel):
    query: str
    tracks: list[UnifiedTrack]


class InteractionCreate(BaseModel):
    username: str
    track: UnifiedTrack
    event_type: Literal["play", "like", "skip", "save_offline"]
    value: float = Field(default=1.0, ge=-5.0, le=5.0)


class PlaybackRequest(BaseModel):
    rate: float = Field(default=1.0, ge=0.5, le=2.0)


class PlaylistImportItem(BaseModel):
    title: str
    artist: str


class PlaylistImportRequest(BaseModel):
    source: Literal["spotify", "soundcloud", "ytmusic", "vkmusic", "telegram"]
    destination: Literal["spotify", "soundcloud", "ytmusic"]
    tracks: list[PlaylistImportItem]


class RecommendationResponse(BaseModel):
    username: str
    tracks: list[UnifiedTrack]
