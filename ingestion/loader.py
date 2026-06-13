"""
Loads raw_data/*.json (produced by spotify_fetch.py or csv_fallback.py)
into PostgreSQL, running schema migrations first.

Usage:
    python loader.py [--reset]   # --reset drops and re-creates all tables
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

RAW_DIR = Path(__file__).parent / "raw_data"
MIGRATIONS_DIR = Path(__file__).parent.parent / "backend" / "migrations"


def get_conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(url)


def run_migration(cur, path: Path) -> None:
    print(f"  Running {path.name}...")
    cur.execute(path.read_text())


def apply_migrations(conn) -> None:
    print("Applying migrations...")
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                name TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            cur.execute("SELECT 1 FROM _migrations WHERE name = %s", (sql_file.name,))
            if cur.fetchone():
                print(f"  Skipping {sql_file.name} (already applied)")
                continue
            run_migration(cur, sql_file)
            cur.execute("INSERT INTO _migrations (name) VALUES (%s)", (sql_file.name,))
    conn.commit()


def reset_schema(conn) -> None:
    print("Resetting schema...")
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS saved_tracks, track_artists, tracks, albums,
                                 artist_genres, genres, artists, _migrations CASCADE
        """)
    conn.commit()


# ─── helpers ──────────────────────────────────────────────────────────────────

def safe_date(val: str | None) -> str | None:
    if not val:
        return None
    for fmt, width in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
        try:
            return datetime.strptime(val[:width], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def upsert_artist(cur, artist: dict) -> None:
    cur.execute("""
        INSERT INTO artists (artist_id, name, popularity, followers)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (artist_id) DO UPDATE
            SET name       = EXCLUDED.name,
                popularity = EXCLUDED.popularity,
                followers  = EXCLUDED.followers
    """, (
        artist["id"],
        artist.get("name", "Unknown"),
        artist.get("popularity", 0),
        (artist.get("followers") or {}).get("total", 0),
    ))

    for genre_name in artist.get("genres", []):
        cur.execute("""
            INSERT INTO genres (name) VALUES (%s)
            ON CONFLICT (name) DO NOTHING
        """, (genre_name,))
        cur.execute("SELECT genre_id FROM genres WHERE name = %s", (genre_name,))
        genre_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO artist_genres (artist_id, genre_id) VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (artist["id"], genre_id))


def upsert_track(cur, track: dict, added_at: str | None = None) -> None:
    album = track.get("album", {})
    album_id = album.get("id")

    if album_id:
        cur.execute("""
            INSERT INTO albums (album_id, name, release_date, album_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (album_id) DO NOTHING
        """, (
            album_id,
            album.get("name", "Unknown"),
            safe_date(album.get("release_date")),
            album.get("album_type", "album"),
        ))

    cur.execute("""
        INSERT INTO tracks (track_id, name, album_id, duration_ms, popularity, explicit)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_id) DO UPDATE
            SET name        = EXCLUDED.name,
                popularity  = EXCLUDED.popularity,
                explicit    = EXCLUDED.explicit
    """, (
        track["id"],
        track.get("name", "Unknown"),
        album_id,
        track.get("duration_ms", 0),
        track.get("popularity", 0),
        bool(track.get("explicit", False)),
    ))

    for artist_stub in track.get("artists", []):
        if artist_stub.get("id"):
            cur.execute("""
                INSERT INTO track_artists (track_id, artist_id) VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (track["id"], artist_stub["id"]))

    if added_at:
        cur.execute("""
            INSERT INTO saved_tracks (track_id, added_at) VALUES (%s, %s)
            ON CONFLICT (track_id) DO NOTHING
        """, (track["id"], added_at))


# ─── loaders ──────────────────────────────────────────────────────────────────

def load_artists(conn) -> None:
    path = RAW_DIR / "artists.json"
    if not path.exists():
        print("  artists.json not found, skipping")
        return
    artists = json.loads(path.read_text())
    print(f"Loading {len(artists)} artists...")
    with conn.cursor() as cur:
        for a in artists:
            upsert_artist(cur, a)
    conn.commit()


def load_saved_tracks(conn) -> None:
    path = RAW_DIR / "saved_tracks.json"
    if not path.exists():
        print("  saved_tracks.json not found, skipping")
        return
    items = json.loads(path.read_text())
    print(f"Loading {len(items)} saved tracks...")
    with conn.cursor() as cur:
        for item in items:
            track = item.get("track") or item
            added_at = item.get("added_at")
            if track and track.get("id"):
                upsert_track(cur, track, added_at)
    conn.commit()


def load_top_tracks(conn) -> None:
    path = RAW_DIR / "top_tracks.json"
    if not path.exists():
        print("  top_tracks.json not found, skipping")
        return
    items = json.loads(path.read_text())
    print(f"Loading {len(items)} top tracks (enriching only, no saved_at)...")
    with conn.cursor() as cur:
        for item in items:
            track = item.get("track") or item
            if track and track.get("id"):
                upsert_track(cur, track, added_at=None)
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")
    args = parser.parse_args()

    conn = get_conn()
    try:
        if args.reset:
            reset_schema(conn)

        apply_migrations(conn)
        load_artists(conn)
        load_saved_tracks(conn)
        load_top_tracks(conn)
        print("\nLoad complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
