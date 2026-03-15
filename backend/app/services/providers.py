from __future__ import annotations

import asyncio
from difflib import SequenceMatcher

import httpx

from app.schemas.music import PlaylistImportItem, UnifiedTrack


class BaseProvider:
    name: str

    async def search(self, query: str, limit: int = 10) -> list[UnifiedTrack]:
        raise NotImplementedError

    async def find_best_match(self, item: PlaylistImportItem) -> UnifiedTrack | None:
        candidates = await self.search(f"{item.artist} {item.title}", limit=5)
        if not candidates:
            return None
        scored = sorted(
            candidates,
            key=lambda tr: SequenceMatcher(None, f"{tr.artist} {tr.title}".lower(), f"{item.artist} {item.title}".lower()).ratio(),
            reverse=True,
        )
        return scored[0]


class SpotifyProvider(BaseProvider):
    name = "spotify"

    async def search(self, query: str, limit: int = 10) -> list[UnifiedTrack]:
        # Demo mock fallback. Replace by official Spotify Web API (OAuth token + /v1/search).
        return [
            UnifiedTrack(
                provider="spotify",
                provider_track_id=f"sp_{i}_{query[:10]}",
                title=f"{query.title()} (Spotify Mix {i})",
                artist="Spotify Artist",
                duration_sec=180 + i,
                genre="pop",
                stream_url="https://p.scdn.co/mp3-preview/example",
            )
            for i in range(1, limit + 1)
        ]


class SoundCloudProvider(BaseProvider):
    name = "soundcloud"

    async def search(self, query: str, limit: int = 10) -> list[UnifiedTrack]:
        return [
            UnifiedTrack(
                provider="soundcloud",
                provider_track_id=f"sc_{i}_{query[:10]}",
                title=f"{query.title()} (Cloud Edit {i})",
                artist="SoundCloud Creator",
                duration_sec=200 + i,
                genre="electronic",
                stream_url="https://soundcloud.com/stream/example",
            )
            for i in range(1, limit + 1)
        ]


class YouTubeMusicProvider(BaseProvider):
    name = "ytmusic"

    async def search(self, query: str, limit: int = 10) -> list[UnifiedTrack]:
        return [
            UnifiedTrack(
                provider="ytmusic",
                provider_track_id=f"yt_{i}_{query[:10]}",
                title=f"{query.title()} (YT Session {i})",
                artist="YouTube Music Channel",
                duration_sec=190 + i,
                genre="hip-hop",
                stream_url="https://music.youtube.com/watch?v=example",
            )
            for i in range(1, limit + 1)
        ]


class UnifiedCatalogService:
    def __init__(self) -> None:
        self.providers: dict[str, BaseProvider] = {
            "spotify": SpotifyProvider(),
            "soundcloud": SoundCloudProvider(),
            "ytmusic": YouTubeMusicProvider(),
        }

    async def aggregate_search(self, query: str, per_provider: int = 5) -> list[UnifiedTrack]:
        tasks = [provider.search(query, per_provider) for provider in self.providers.values()]
        results = await asyncio.gather(*tasks)
        merged = [track for subset in results for track in subset]
        return merged

    async def import_playlist(
        self,
        destination: str,
        tracks: list[PlaylistImportItem],
    ) -> list[UnifiedTrack]:
        destination_provider = self.providers[destination]
        matched: list[UnifiedTrack] = []
        for item in tracks:
            best = await destination_provider.find_best_match(item)
            if best:
                matched.append(best)
        return matched
