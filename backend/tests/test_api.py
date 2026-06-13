"""Tests for all five API endpoints using mocked psycopg2 connection."""

import pytest
from contextlib import ExitStack
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

# Patch targets — routes bind db_cursor locally via `from ... import`
_ROUTE_MODULES = [
    "app.api.stats.db_cursor",
    "app.api.genres.db_cursor",
    "app.api.popularity.db_cursor",
    "app.api.artists.db_cursor",
    "app.api.duration.db_cursor",
]


def make_cursor(rows):
    cur = MagicMock()
    cur.__enter__ = lambda s: cur
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = rows[0] if rows else None
    cur.fetchall.return_value = rows
    return cur


class patch_cursor:
    """Context manager that patches db_cursor in every route module at once."""

    def __init__(self, rows):
        self._rows = rows
        self._stack = ExitStack()

    def __enter__(self):
        cur = make_cursor(self._rows)
        for target in _ROUTE_MODULES:
            self._stack.enter_context(patch(target, return_value=cur))
        return cur

    def __exit__(self, *args):
        self._stack.close()


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestSummary:
    def test_returns_summary(self):
        row = {"total_tracks": 100, "total_artists": 30, "total_genres": 12}
        with patch_cursor([row]):
            r = client.get("/api/stats/summary")
        assert r.status_code == 200
        data = r.json()
        assert data["total_tracks"] == 100
        assert data["total_artists"] == 30
        assert data["total_genres"] == 12

    def test_no_data_returns_404(self):
        with patch_cursor([]):
            r = client.get("/api/stats/summary")
        assert r.status_code == 404


class TestGenres:
    def test_returns_list(self):
        rows = [
            {"genre": "pop", "track_count": 42},
            {"genre": "rock", "track_count": 18},
        ]
        with patch_cursor(rows):
            r = client.get("/api/genres/distribution")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 2
        assert body[0]["genre"] == "pop"

    def test_empty_list(self):
        with patch_cursor([]):
            r = client.get("/api/genres/distribution")
        assert r.status_code == 200
        assert r.json() == []


class TestPopularity:
    def test_returns_decades(self):
        rows = [
            {"decade": 1990, "avg_popularity": 65.2, "track_count": 10},
            {"decade": 2000, "avg_popularity": 72.5, "track_count": 25},
        ]
        with patch_cursor(rows):
            r = client.get("/api/popularity/by-decade")
        assert r.status_code == 200
        body = r.json()
        assert body[0]["decade"] == 1990
        assert body[1]["avg_popularity"] == 72.5


class TestArtists:
    def test_returns_ranked_artists(self):
        rows = [
            {"name": "Artist A", "artist_popularity": 88, "track_count": 15, "rnk": 1},
            {"name": "Artist B", "artist_popularity": 74, "track_count": 10, "rnk": 2},
        ]
        with patch_cursor(rows):
            r = client.get("/api/artists/top")
        assert r.status_code == 200
        body = r.json()
        assert body[0]["rnk"] == 1
        assert body[1]["name"] == "Artist B"

    def test_limit_param(self):
        rows = [{"name": "A", "artist_popularity": 80, "track_count": 5, "rnk": 1}]
        with patch_cursor(rows):
            r = client.get("/api/artists/top?limit=1")
        assert r.status_code == 200


class TestDuration:
    def test_returns_genres_with_duration(self):
        rows = [
            {"genre": "jazz", "avg_duration_sec": 245.5, "track_count": 8},
            {"genre": "pop",  "avg_duration_sec": 198.2, "track_count": 40},
        ]
        with patch_cursor(rows):
            r = client.get("/api/duration/by-genre")
        assert r.status_code == 200
        body = r.json()
        assert body[0]["genre"] == "jazz"
        assert body[0]["avg_duration_sec"] == 245.5
