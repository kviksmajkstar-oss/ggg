from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Interaction, Track, User
from app.recommendations.engine import Recommender
from app.schemas.music import (
    InteractionCreate,
    PlaybackRequest,
    PlaylistImportRequest,
    RecommendationResponse,
    SearchResponse,
    UnifiedTrack,
)
from app.services.providers import UnifiedCatalogService

router = APIRouter(prefix="/api", tags=["music"])
service = UnifiedCatalogService()
recommender = Recommender()


@router.get("/search", response_model=SearchResponse)
async def search(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    tracks = await service.aggregate_search(query)
    _upsert_tracks(db, tracks)
    return SearchResponse(query=query, tracks=tracks)


@router.post("/interaction")
def add_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user:
        user = User(username=payload.username)
        db.add(user)
        db.flush()

    track = db.scalar(
        select(Track).where(
            Track.provider == payload.track.provider,
            Track.provider_track_id == payload.track.provider_track_id,
        )
    )
    if not track:
        track = Track(**payload.track.model_dump())
        db.add(track)
        db.flush()

    interaction = Interaction(user_id=user.id, track_id=track.id, event_type=payload.event_type, value=payload.value)
    db.add(interaction)
    db.commit()

    return {"status": "ok"}


@router.get("/recommendations/{username}", response_model=RecommendationResponse)
def recommendations(username: str, db: Session = Depends(get_db)):
    tracks = recommender.recommend_for_user(db, username=username)
    return RecommendationResponse(username=username, tracks=tracks)


@router.post("/playback/transform")
def transform_playback(payload: PlaybackRequest):
    # Реальное замедление/ускорение для стриминга чаще делается на клиенте через HTMLAudioElement.playbackRate
    preset = "slowed" if payload.rate < 1.0 else "sped_up" if payload.rate > 1.0 else "normal"
    return {"rate": payload.rate, "preset": preset}


@router.post("/playlist/import")
async def import_playlist(payload: PlaylistImportRequest):
    tracks = await service.import_playlist(destination=payload.destination, tracks=payload.tracks)
    return {"destination": payload.destination, "matched": tracks}


def _upsert_tracks(db: Session, tracks: list[UnifiedTrack]) -> None:
    for tr in tracks:
        exists = db.scalar(
            select(Track).where(Track.provider == tr.provider, Track.provider_track_id == tr.provider_track_id)
        )
        if exists:
            continue
        db.add(Track(**tr.model_dump()))
    db.commit()
