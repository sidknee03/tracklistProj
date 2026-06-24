"""Tests for seed data helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ingestion"))

from seed import PLATFORMS, ARTISTS, GENRES, TRACKS, PERIODS


class TestReferenceData:
    def test_all_platforms_have_rate(self):
        for name, model, rate in PLATFORMS:
            assert rate > 0, f"{name} has zero rate"

    def test_purchase_platforms_have_high_rate(self):
        for name, model, rate in PLATFORMS:
            if model == "purchase":
                assert rate > 0.5, f"{name} purchase rate should be >50%"

    def test_stream_platforms_have_low_rate(self):
        for name, model, rate in PLATFORMS:
            if model == "stream":
                assert rate < 0.05, f"{name} stream rate should be <$0.05"

    def test_tidal_pays_more_than_spotify(self):
        rates = {name: rate for name, _, rate in PLATFORMS if _ == "stream"}
        assert rates["Tidal"] > rates["Spotify"]

    def test_apple_music_pays_more_than_youtube(self):
        rates = {name: rate for name, _, rate in PLATFORMS if _ == "stream"}
        assert rates["Apple Music"] > rates["YouTube Music"]

    def test_artists_have_country(self):
        for name, country in ARTISTS:
            assert len(country) == 2, f"{name} country code should be 2 chars"

    def test_24_months_of_periods(self):
        assert len(PERIODS) == 24

    def test_periods_are_sorted(self):
        assert PERIODS == sorted(PERIODS)

    def test_periods_span_2023_2024(self):
        assert PERIODS[0] == "2023-01"
        assert PERIODS[-1] == "2024-12"

    def test_no_duplicate_tracks(self):
        assert len(TRACKS) == len(set(TRACKS))
