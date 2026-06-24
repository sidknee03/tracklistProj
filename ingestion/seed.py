"""
Generates synthetic streaming royalty data and loads it into data/music.db.
No credentials or files needed — just run it.

Usage:
    python seed.py [--reset]
"""

import argparse
import random
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.connection import db_cursor, is_postgres, SQLITE_PATH

MIGRATIONS_DIR = Path(__file__).parent.parent / "backend" / "migrations"
PH = "%s" if is_postgres() else "?"
random.seed(42)

# ── reference data ─────────────────────────────────────────────────────────────

PLATFORMS = [
    ("Spotify",       "stream",   0.004),
    ("Apple Music",   "stream",   0.008),
    ("Tidal",         "stream",   0.013),
    ("Amazon Music",  "stream",   0.004),
    ("YouTube Music", "stream",   0.002),
    ("Deezer",        "stream",   0.006),
    ("SoundCloud",    "stream",   0.003),
    ("Pandora",       "stream",   0.0013),
    ("Bandcamp",      "purchase", 0.82),
]

ARTISTS = [
    ("Nova Hayes",       "CA"), ("Kade Williams",    "US"), ("Stella Park",      "US"),
    ("Jade Monroe",      "US"), ("BLVCK PLVNET",     "DE"), ("Hollow Kings",     "US"),
    ("Valentina Cruz",   "MX"), ("Marcus Bell Trio", "US"), ("Paper Boats",      "GB"),
    ("Tyler Wade",       "US"), ("Iron Veil",        "SE"), ("Mira Sol",         "CA"),
    ("Neon Drift",       "FR"), ("The Static",       "GB"), ("Elaine Cho",       "KR"),
    ("Red Rust",         "AU"), ("Brynn Carter",     "CA"), ("Cleo Marsh",       "AU"),
    ("Alex Cross",       "US"), ("Rayo",             "CO"),
]

GENRES = ["Pop", "Hip-Hop", "R&B", "Rock", "Electronic", "Country", "Jazz", "Indie", "Metal", "Latin"]

TRACKS = [
    "Golden Hour", "On the Grind", "Slow Motion", "Fracture", "System Fault",
    "Dirt Roads", "Blue Reverie", "Hollow Sun", "Iron Crown", "Fuego",
    "Neon Signs", "Real Talk", "All Night", "Alive Again", "Phase Shift",
    "Home Again", "Midnight Session", "Soft Landing", "The Abyss", "La Noche",
    "Stay the Night", "Levels", "Body Language", "Undertow", "Drift",
    "Southern Rain", "Interlude", "Colour Blind", "Warpath", "Sin Ti",
]

PERIODS = [
    "2023-01","2023-02","2023-03","2023-04","2023-05","2023-06",
    "2023-07","2023-08","2023-09","2023-10","2023-11","2023-12",
    "2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
    "2024-07","2024-08","2024-09","2024-10","2024-11","2024-12",
]

# ── migrations ─────────────────────────────────────────────────────────────────

def apply_migrations():
    print("Running migrations...")
    with db_cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY)")
        for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
            cur.execute(f"SELECT 1 FROM _migrations WHERE name = {PH}", (f.name,))
            if cur.fetchone():
                continue
            print(f"  {f.name}")
            for stmt in [s.strip() for s in f.read_text().split(";") if s.strip()]:
                cur.execute(stmt)
            cur.execute(f"INSERT INTO _migrations (name) VALUES ({PH})", (f.name,))


def reset_schema():
    print("Resetting...")
    with db_cursor() as cur:
        for t in ["streams","tracks","artist_genres","genres","artists","platforms","_migrations"]:
            cur.execute(f"DROP TABLE IF EXISTS {t}")
        for v in ["v_summary","v_platform_revenue","v_artist_earnings","v_genre_revenue","v_monthly_revenue","v_platform_efficiency"]:
            cur.execute(f"DROP VIEW IF EXISTS {v}")


# ── seed ───────────────────────────────────────────────────────────────────────

def seed():
    print("Seeding data...")
    with db_cursor() as cur:
        # platforms
        for name, model, rate in PLATFORMS:
            cur.execute(
                f"INSERT INTO platforms (name,model,rate_per_unit) VALUES ({PH},{PH},{PH}) ON CONFLICT(name) DO NOTHING",
                (name, model, rate)
            )

        # genres
        for g in GENRES:
            cur.execute(f"INSERT INTO genres (name) VALUES ({PH}) ON CONFLICT(name) DO NOTHING", (g,))

        # artists + genre mapping
        artist_ids = {}
        for name, country in ARTISTS:
            aid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
            artist_ids[name] = aid
            listeners = random.randint(5_000, 1_500_000)
            cur.execute(
                f"INSERT INTO artists (artist_id,name,country,monthly_listeners) VALUES ({PH},{PH},{PH},{PH}) ON CONFLICT DO NOTHING",
                (aid, name, country, listeners)
            )
            # assign 1-2 genres per artist
            cur.execute(f"SELECT genre_id FROM genres ORDER BY RANDOM() LIMIT 2")
            for row in cur.fetchall():
                cur.execute(
                    f"INSERT INTO artist_genres (artist_id,genre_id) VALUES ({PH},{PH}) ON CONFLICT DO NOTHING",
                    (aid, row[0])
                )

        # tracks — 1-2 per artist from the pool
        track_ids = {}
        artist_list = list(artist_ids.items())
        for i, title in enumerate(TRACKS):
            artist_name, aid = artist_list[i % len(artist_list)]
            tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{artist_name}:{title}"))
            track_ids[title] = tid
            release = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            cur.execute(
                f"INSERT INTO tracks (track_id,artist_id,title,duration_ms,release_date,explicit) VALUES ({PH},{PH},{PH},{PH},{PH},{PH}) ON CONFLICT DO NOTHING",
                (tid, aid, title, random.randint(150_000, 320_000), release, random.choice([0,0,0,1]))
            )

        # streams — for each track × platform × month
        cur.execute(f"SELECT platform_id, name, model, rate_per_unit FROM platforms")
        platform_rows = cur.fetchall()

        for title, tid in track_ids.items():
            for prow in platform_rows:
                pid, pname, model, rate = prow[0], prow[1], prow[2], prow[3]
                for period in PERIODS:
                    if model == "purchase":
                        units   = random.randint(0, 25)
                        revenue = round(units * random.uniform(5, 12) * rate, 2)
                    else:
                        units   = random.randint(500, 250_000)
                        revenue = round(units * rate, 2)
                    if units == 0:
                        continue
                    cur.execute(
                        f"INSERT INTO streams (track_id,platform_id,period,units,revenue) VALUES ({PH},{PH},{PH},{PH},{PH}) ON CONFLICT DO NOTHING",
                        (tid, pid, period, units, revenue)
                    )

    print("Done.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    print(f"Target: {'Postgres' if is_postgres() else f'SQLite ({SQLITE_PATH})'}\n")
    if args.reset:
        reset_schema()
    apply_migrations()
    seed()

    with db_cursor() as cur:
        cur.execute("SELECT total_artists, total_tracks, total_platforms, total_revenue_usd, total_streams FROM v_summary")
        r = cur.fetchone()
        print(f"\n  artists: {r[0]}  tracks: {r[1]}  platforms: {r[2]}")
        print(f"  revenue: ${r[3]:,.2f}  streams: {r[4]:,}")


if __name__ == "__main__":
    main()
