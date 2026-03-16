from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Interaction, Track, User
from app.schemas.music import UnifiedTrack

EVENT_WEIGHTS = {
    "play": 1.0,
    "like": 3.0,
    "save_offline": 2.0,
    "skip": -1.5,
}


class Recommender:
    def recommend_for_user(self, db: Session, username: str, limit: int = 20) -> list[UnifiedTrack]:
        user = db.scalar(select(User).where(User.username == username))
        if not user:
            return self._cold_start(db, limit)

        interactions = db.scalars(select(Interaction).where(Interaction.user_id == user.id)).all()
        if not interactions:
            return self._cold_start(db, limit)

        user_genre_scores = defaultdict(float)
        listened_track_ids = set()

        for i in interactions:
            track = db.get(Track, i.track_id)
            if not track:
                continue
            weight = EVENT_WEIGHTS.get(i.event_type, 0.0) * i.value
            user_genre_scores[track.genre] += weight
            listened_track_ids.add(track.id)

        candidates = db.scalars(select(Track)).all()
        ranked = sorted(
            (c for c in candidates if c.id not in listened_track_ids),
            key=lambda t: self._score_track(t, user_genre_scores),
            reverse=True,
        )

        return [
            UnifiedTrack(
                provider=t.provider,
                provider_track_id=t.provider_track_id,
                title=t.title,
                artist=t.artist,
                duration_sec=t.duration_sec,
                genre=t.genre,
                stream_url=t.stream_url,
            )
            for t in ranked[:limit]
        ]

    @staticmethod
    def _score_track(track: Track, user_genre_scores: dict[str, float]) -> float:
        base = user_genre_scores.get(track.genre, 0.0)
        duration_bonus = max(0.0, 1.0 - abs(track.duration_sec - 210) / 300)
        return base + duration_bonus

    @staticmethod
    def _cold_start(db: Session, limit: int) -> list[UnifiedTrack]:
        trending = db.scalars(select(Track).limit(limit)).all()
        return [
            UnifiedTrack(
                provider=t.provider,
                provider_track_id=t.provider_track_id,
                title=t.title,
                artist=t.artist,
                duration_sec=t.duration_sec,
                genre=t.genre,
                stream_url=t.stream_url,
            )
            for t in trending
        ]
