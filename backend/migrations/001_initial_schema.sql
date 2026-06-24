-- Migration 001: Streaming royalty analytics schema
-- SQLite by default. For Postgres: AUTOINCREMENT→SERIAL, TEXT dates→DATE/TIMESTAMPTZ.

CREATE TABLE IF NOT EXISTS platforms (
    platform_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    model         TEXT NOT NULL CHECK(model IN ('stream','purchase')),
    rate_per_unit REAL NOT NULL   -- $ per stream, or artist revenue share (0-1) for purchase
);

CREATE TABLE IF NOT EXISTS artists (
    artist_id        TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    country          TEXT,
    monthly_listeners INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS artist_genres (
    artist_id TEXT    NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    genre_id  INTEGER NOT NULL REFERENCES genres(genre_id)  ON DELETE CASCADE,
    PRIMARY KEY (artist_id, genre_id)
);

CREATE TABLE IF NOT EXISTS tracks (
    track_id     TEXT PRIMARY KEY,
    artist_id    TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    duration_ms  INTEGER DEFAULT 0,
    release_date TEXT,
    explicit     INTEGER DEFAULT 0
);

-- One row per track × platform × month.
-- units = streams (streaming) or purchases (Bandcamp/purchase model)
-- revenue = pre-calculated royalty payout in USD
CREATE TABLE IF NOT EXISTS streams (
    stream_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id    TEXT    NOT NULL REFERENCES tracks(track_id)    ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES platforms(platform_id) ON DELETE CASCADE,
    period      TEXT    NOT NULL,  -- 'YYYY-MM'
    units       INTEGER NOT NULL DEFAULT 0,
    revenue     REAL    NOT NULL DEFAULT 0.0
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_streams_unique   ON streams(track_id, platform_id, period);
CREATE INDEX        IF NOT EXISTS idx_streams_period   ON streams(period);
CREATE INDEX        IF NOT EXISTS idx_streams_platform ON streams(platform_id);
CREATE INDEX        IF NOT EXISTS idx_tracks_artist    ON tracks(artist_id);
CREATE INDEX        IF NOT EXISTS idx_artist_genres_g  ON artist_genres(genre_id);
