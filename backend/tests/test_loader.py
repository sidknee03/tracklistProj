"""Tests for ingestion transform helpers (safe_date, upsert logic)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ingestion"))

from loader import safe_date


class TestSafeDate:
    def test_full_date(self):
        assert safe_date("2020-06-15") == "2020-06-15"

    def test_year_month(self):
        assert safe_date("1999-03") == "1999-03-01"

    def test_year_only(self):
        assert safe_date("1985") == "1985-01-01"

    def test_none_returns_none(self):
        assert safe_date(None) is None

    def test_empty_returns_none(self):
        assert safe_date("") is None

    def test_garbage_returns_none(self):
        assert safe_date("not-a-date") is None


class TestCSVFallback:
    """Verify csv_fallback converts rows into the expected raw_data structure."""

    def _make_row(self, **kwargs):
        defaults = {
            "track_id": "t1", "track_name": "Song", "artist_name": "Band",
            "album": "Alb", "release_date": "2010-01-01",
            "duration_ms": "200000", "popularity": "70", "explicit": "0",
            "genres": "rock;pop", "artist_popularity": "80", "followers": "5000",
        }
        return {**defaults, **kwargs}

    def test_csv_fallback_builds_artist(self):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ingestion"))
        from csv_fallback import build_artist

        row = self._make_row()
        artist = build_artist(row, "a1")
        assert artist["id"] == "a1"
        assert artist["name"] == "Band"
        assert artist["genres"] == ["rock", "pop"]
        assert artist["popularity"] == 80

    def test_csv_fallback_builds_track(self):
        from csv_fallback import build_track

        row = self._make_row()
        track = build_track(row, "a1")
        assert track["id"] == "t1"
        assert track["name"] == "Song"
        assert track["duration_ms"] == 200000
        assert track["explicit"] is False
        assert track["album"]["name"] == "Alb"

    def test_explicit_flag_true(self):
        from csv_fallback import build_track

        row = self._make_row(explicit="1")
        track = build_track(row, "a1")
        assert track["explicit"] is True
