-- Migration 001: Initial schema
-- Normalized music analytics schema

CREATE TABLE IF NOT EXISTS artists (
    artist_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    popularity  INTEGER DEFAULT 0 CHECK (popularity BETWEEN 0 AND 100),
    followers   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS genres (
    genre_id    SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS artist_genres (
    artist_id   TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    genre_id    INTEGER NOT NULL REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (artist_id, genre_id)
);

CREATE TABLE IF NOT EXISTS albums (
    album_id     TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    release_date DATE,
    album_type   TEXT DEFAULT 'album'
);

CREATE TABLE IF NOT EXISTS tracks (
    track_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    album_id    TEXT REFERENCES albums(album_id) ON DELETE SET NULL,
    duration_ms INTEGER DEFAULT 0,
    popularity  INTEGER DEFAULT 0 CHECK (popularity BETWEEN 0 AND 100),
    explicit    BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS track_artists (
    track_id    TEXT NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    artist_id   TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, artist_id)
);

CREATE TABLE IF NOT EXISTS saved_tracks (
    track_id    TEXT PRIMARY KEY REFERENCES tracks(track_id) ON DELETE CASCADE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common join paths
CREATE INDEX IF NOT EXISTS idx_track_artists_artist ON track_artists(artist_id);
CREATE INDEX IF NOT EXISTS idx_artist_genres_genre  ON artist_genres(genre_id);
CREATE INDEX IF NOT EXISTS idx_tracks_album          ON tracks(album_id);
CREATE INDEX IF NOT EXISTS idx_saved_tracks_added    ON saved_tracks(added_at);
