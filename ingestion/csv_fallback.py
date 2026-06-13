"""
Fallback: converts a Kaggle Spotify tracks CSV into the same raw_data format
that loader.py expects, so the rest of the pipeline is identical.

Expected CSV columns (from https://www.kaggle.com/datasets/lehaknarnauli/spotify-datasets):
  track_id, track_name, artist_name, album, release_date, duration_ms,
  popularity, explicit, genres (semicolon-separated)

Usage:
    python csv_fallback.py --csv path/to/tracks.csv
"""

import argparse
import csv
import json
import uuid
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw_data"
RAW_DIR.mkdir(exist_ok=True)


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_artist(row: dict, artist_id: str) -> dict:
    return {
        "id": artist_id,
        "name": row.get("artist_name", "Unknown"),
        "popularity": int(row.get("artist_popularity", 50)),
        "followers": {"total": int(row.get("followers", 0))},
        "genres": [g.strip() for g in row.get("genres", "").split(";") if g.strip()],
    }


def build_track(row: dict, artist_id: str) -> dict:
    return {
        "id": row.get("track_id") or str(uuid.uuid4()),
        "name": row.get("track_name", "Unknown"),
        "duration_ms": int(row.get("duration_ms", 0)),
        "popularity": int(row.get("popularity", 0)),
        "explicit": str(row.get("explicit", "0")) in ("1", "True", "true"),
        "artists": [{"id": artist_id, "name": row.get("artist_name", "Unknown")}],
        "album": {
            "id": str(uuid.uuid4()),
            "name": row.get("album", "Unknown"),
            "release_date": row.get("release_date", "2000-01-01"),
            "album_type": "album",
        },
    }


def convert(csv_path: str) -> None:
    rows = load_csv(csv_path)
    print(f"Loaded {len(rows)} CSV rows")

    artists_by_name: dict[str, dict] = {}
    saved_tracks = []
    top_tracks = []

    for row in rows:
        artist_name = row.get("artist_name", "Unknown")
        if artist_name not in artists_by_name:
            artists_by_name[artist_name] = build_artist(row, str(uuid.uuid4()))

        artist_id = artists_by_name[artist_name]["id"]
        track = build_track(row, artist_id)

        # Wrap as saved_track object (added_at synthetic)
        saved_tracks.append({"added_at": row.get("added_at", "2023-01-01T00:00:00Z"), "track": track})

        # Also expose as top_track (flat format)
        top_tracks.append(track)

    artists = list(artists_by_name.values())

    (RAW_DIR / "saved_tracks.json").write_text(json.dumps(saved_tracks, indent=2))
    (RAW_DIR / "top_tracks.json").write_text(json.dumps(top_tracks, indent=2))
    (RAW_DIR / "artists.json").write_text(json.dumps(artists, indent=2))

    print(f"Wrote raw_data/: {len(saved_tracks)} tracks, {len(artists)} artists")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to Kaggle CSV file")
    args = parser.parse_args()
    convert(args.csv)
