"""
Fetches saved tracks, top tracks, and playlist tracks from Spotify API.
Writes raw JSON responses to ingestion/raw_data/ for the loader to consume.

Usage:
    python spotify_fetch.py

Requires SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI in .env
"""

import json
import os
import time
from pathlib import Path

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv(Path(__file__).parent.parent / ".env")

RAW_DIR = Path(__file__).parent / "raw_data"
RAW_DIR.mkdir(exist_ok=True)

SCOPE = " ".join([
    "user-library-read",
    "user-top-read",
    "playlist-read-private",
])


def build_client() -> spotipy.Spotify:
    cache_path = Path(__file__).parent / "tokens" / ".spotify_cache"
    cache_path.parent.mkdir(exist_ok=True)
    auth = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=SCOPE,
        cache_path=str(cache_path),
    )
    return spotipy.Spotify(auth_manager=auth)


def paginate(sp_method, **kwargs) -> list[dict]:
    results = []
    response = sp_method(limit=50, **kwargs)
    while response:
        items = response.get("items", [])
        results.extend(items)
        response = sp_method(limit=50, offset=len(results), **kwargs) if response.get("next") else None
        if response:
            time.sleep(0.1)
    return results


def fetch_saved_tracks(sp: spotipy.Spotify) -> list[dict]:
    print("Fetching saved tracks...")
    items = paginate(sp.current_user_saved_tracks)
    print(f"  -> {len(items)} saved tracks")
    return items


def fetch_top_tracks(sp: spotipy.Spotify) -> list[dict]:
    print("Fetching top tracks...")
    results = []
    for time_range in ("short_term", "medium_term", "long_term"):
        resp = sp.current_user_top_tracks(limit=50, time_range=time_range)
        results.extend(resp.get("items", []))
    print(f"  -> {len(results)} top track entries")
    return results


def fetch_artist_details(sp: spotipy.Spotify, artist_ids: list[str]) -> list[dict]:
    print(f"Fetching details for {len(artist_ids)} artists...")
    artists = []
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i : i + 50]
        resp = sp.artists(batch)
        artists.extend(resp.get("artists", []))
        time.sleep(0.1)
    return artists


def main() -> None:
    sp = build_client()

    saved = fetch_saved_tracks(sp)
    (RAW_DIR / "saved_tracks.json").write_text(json.dumps(saved, indent=2))

    top = fetch_top_tracks(sp)
    (RAW_DIR / "top_tracks.json").write_text(json.dumps(top, indent=2))

    # Collect unique artist IDs across all tracks
    all_tracks = saved + top
    artist_ids = list({
        a["id"]
        for item in all_tracks
        for a in (item.get("track") or item).get("artists", [])
        if a.get("id")
    })

    artists = fetch_artist_details(sp, artist_ids)
    (RAW_DIR / "artists.json").write_text(json.dumps(artists, indent=2))

    print(f"\nRaw data written to {RAW_DIR}")
    print(f"  saved_tracks.json  -> {len(saved)} items")
    print(f"  top_tracks.json    -> {len(top)} items")
    print(f"  artists.json       -> {len(artists)} artists")


if __name__ == "__main__":
    main()
