"""
Loads raw_data/*.json into the local SQLite database (data/music.db) by default.
Set DATABASE_URL=postgresql://... to target Postgres/RDS instead.

Usage:
    python loader.py [--reset]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Add backend to path so we can import from app.db
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.connection import db_cursor, is_postgres, SQLITE_PATH

RAW_DIR       = Path(__file__).parent / "raw_data"
MIGRATIONS_DIR = Path(__file__).parent.parent / "backend" / "migrations"

PH = "%s" if is_postgres() else "?"


# ─── migration runner ─────────────────────────────────────────────────────────

def apply_migrations() -> None:
    print("Applying migrations...")
    with db_cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS _migrations (
                name TEXT PRIMARY KEY,
                applied_at TEXT DEFAULT (datetime('now'))
            )
        """)

        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            cur.execute(f"SELECT 1 FROM _migrations WHERE name = {PH}", (sql_file.name,))
            if cur.fetchone():
                print(f"  skip {sql_file.name}")
                continue
            print(f"  run  {sql_file.name}")
            # SQLite needs statements executed one at a time
            statements = [s.strip() for s in sql_file.read_text().split(";") if s.strip()]
            for stmt in statements:
                cur.execute(stmt)
            cur.execute(f"INSERT INTO _migrations (name) VALUES ({PH})", (sql_file.name,))


def reset_schema() -> None:
    print("Resetting schema...")
    tables = ["saved_tracks", "track_artists", "tracks", "albums",
              "artist_genres", "genres", "artists", "_migrations"]
    with db_cursor() as cur:
        for t in tables:
            cur.execute(f"DROP TABLE IF EXISTS {t}")
        views = ["v_genre_distribution", "v_popularity_by_decade", "v_top_artists",
                 "v_duration_by_genre", "v_explicit_ratio", "v_tracks_over_time", "v_summary"]
        for v in views:
            cur.execute(f"DROP VIEW IF EXISTS {v}")


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
    cur.execute(f"""
        INSERT INTO artists (artist_id, name, popularity, followers)
        VALUES ({PH},{PH},{PH},{PH})
        ON CONFLICT(artist_id) DO UPDATE SET
            name=excluded.name, popularity=excluded.popularity, followers=excluded.followers
    """, (
        artist["id"],
        artist.get("name", "Unknown"),
        artist.get("popularity", 0),
        (artist.get("followers") or {}).get("total", 0),
    ))

    for genre_name in artist.get("genres", []):
        cur.execute(f"INSERT INTO genres (name) VALUES ({PH}) ON CONFLICT(name) DO NOTHING", (genre_name,))
        cur.execute(f"SELECT genre_id FROM genres WHERE name = {PH}", (genre_name,))
        row = cur.fetchone()
        genre_id = row[0] if row else None
        if genre_id:
            cur.execute(f"""
                INSERT INTO artist_genres (artist_id, genre_id) VALUES ({PH},{PH})
                ON CONFLICT DO NOTHING
            """, (artist["id"], genre_id))


def upsert_track(cur, track: dict, added_at: str | None = None) -> None:
    album    = track.get("album", {})
    album_id = album.get("id")

    if album_id:
        cur.execute(f"""
            INSERT INTO albums (album_id, name, release_date, album_type)
            VALUES ({PH},{PH},{PH},{PH})
            ON CONFLICT(album_id) DO NOTHING
        """, (album_id, album.get("name", "Unknown"),
              safe_date(album.get("release_date")), album.get("album_type", "album")))

    cur.execute(f"""
        INSERT INTO tracks (track_id, name, album_id, duration_ms, popularity, explicit)
        VALUES ({PH},{PH},{PH},{PH},{PH},{PH})
        ON CONFLICT(track_id) DO UPDATE SET
            name=excluded.name, popularity=excluded.popularity, explicit=excluded.explicit
    """, (
        track["id"],
        track.get("name", "Unknown"),
        album_id,
        track.get("duration_ms", 0),
        track.get("popularity", 0),
        int(bool(track.get("explicit", False))),
    ))

    for artist_stub in track.get("artists", []):
        if artist_stub.get("id"):
            cur.execute(f"""
                INSERT INTO track_artists (track_id, artist_id) VALUES ({PH},{PH})
                ON CONFLICT DO NOTHING
            """, (track["id"], artist_stub["id"]))

    if added_at:
        cur.execute(f"""
            INSERT INTO saved_tracks (track_id, added_at) VALUES ({PH},{PH})
            ON CONFLICT(track_id) DO NOTHING
        """, (track["id"], added_at))


# ─── loaders ──────────────────────────────────────────────────────────────────

def load_artists() -> None:
    path = RAW_DIR / "artists.json"
    if not path.exists():
        print("  artists.json not found, skipping"); return
    artists = json.loads(path.read_text())
    print(f"Loading {len(artists)} artists...")
    with db_cursor() as cur:
        for a in artists:
            upsert_artist(cur, a)


def load_saved_tracks() -> None:
    path = RAW_DIR / "saved_tracks.json"
    if not path.exists():
        print("  saved_tracks.json not found, skipping"); return
    items = json.loads(path.read_text())
    print(f"Loading {len(items)} saved tracks...")
    with db_cursor() as cur:
        for item in items:
            track    = item.get("track") or item
            added_at = item.get("added_at")
            if track and track.get("id"):
                upsert_track(cur, track, added_at)


def load_top_tracks() -> None:
    path = RAW_DIR / "top_tracks.json"
    if not path.exists():
        print("  top_tracks.json not found, skipping"); return
    items = json.loads(path.read_text())
    print(f"Loading {len(items)} top tracks...")
    with db_cursor() as cur:
        for item in items:
            track = item.get("track") or item
            if track and track.get("id"):
                upsert_track(cur, track, added_at=None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    db_label = "Postgres" if is_postgres() else f"SQLite ({SQLITE_PATH})"
    print(f"Target: {db_label}\n")

    if args.reset:
        reset_schema()

    apply_migrations()
    load_artists()
    load_saved_tracks()
    load_top_tracks()
    print("\nDone.")


if __name__ == "__main__":
    main()
