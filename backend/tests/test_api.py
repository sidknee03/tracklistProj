"""Tests for all API endpoints using mocked DB cursor."""

from contextlib import ExitStack
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

_ROUTE_MODULES = [
    "app.api.summary.db_cursor",
    "app.api.platforms.db_cursor",
    "app.api.artists.db_cursor",
    "app.api.genres.db_cursor",
    "app.api.trends.db_cursor",
]


def make_cursor(rows):
    cur = MagicMock()
    cur.__enter__ = lambda s: cur
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = rows[0] if rows else None
    cur.fetchall.return_value = rows
    return cur


class patch_cursor:
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
        row = {"total_artists": 25, "total_tracks": 150, "total_platforms": 9,
               "total_revenue_usd": 48320.50, "total_streams": 12_000_000}
        with patch_cursor([row]):
            r = client.get("/api/summary")
        assert r.status_code == 200
        data = r.json()
        assert data["total_artists"] == 25
        assert data["total_platforms"] == 9

    def test_no_data_returns_404(self):
        with patch_cursor([]):
            r = client.get("/api/summary")
        assert r.status_code == 404


class TestPlatforms:
    def test_revenue_returns_list(self):
        rows = [
            {"platform": "Spotify", "model": "stream", "rate_per_unit": 0.004,
             "total_units": 5_000_000, "total_revenue": 20000.0, "revenue_rank": 1},
            {"platform": "Tidal", "model": "stream", "rate_per_unit": 0.013,
             "total_units": 200_000, "total_revenue": 2600.0, "revenue_rank": 2},
        ]
        with patch_cursor(rows):
            r = client.get("/api/platforms/revenue")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 2
        assert body[0]["platform"] == "Spotify"
        assert body[1]["revenue_rank"] == 2

    def test_efficiency_returns_list(self):
        rows = [{"name": "Tidal", "model": "stream", "published_rate": 0.013,
                 "actual_rate": 0.013, "total_revenue": 2600.0, "total_units": 200_000}]
        with patch_cursor(rows):
            r = client.get("/api/platforms/efficiency")
        assert r.status_code == 200


class TestArtists:
    def test_top_artists(self):
        rows = [
            {"name": "Nova Hayes", "country": "CA", "monthly_listeners": 800_000,
             "total_revenue": 9200.0, "total_units": 2_300_000, "rnk": 1},
        ]
        with patch_cursor(rows):
            r = client.get("/api/artists/top")
        assert r.status_code == 200
        body = r.json()
        assert body[0]["rnk"] == 1
        assert body[0]["country"] == "CA"


class TestGenres:
    def test_genre_revenue(self):
        rows = [
            {"genre": "Pop", "total_revenue": 15000.0, "total_units": 3_000_000,
             "track_count": 40, "artist_count": 6},
        ]
        with patch_cursor(rows):
            r = client.get("/api/genres/revenue")
        assert r.status_code == 200
        assert r.json()[0]["genre"] == "Pop"


class TestTrends:
    def test_monthly_trend(self):
        rows = [
            {"period": "2023-01", "monthly_revenue": 1200.0, "running_total": 1200.0},
            {"period": "2023-02", "monthly_revenue": 1500.0, "running_total": 2700.0},
        ]
        with patch_cursor(rows):
            r = client.get("/api/trends/monthly")
        assert r.status_code == 200
        body = r.json()
        assert body[1]["running_total"] == 2700.0
