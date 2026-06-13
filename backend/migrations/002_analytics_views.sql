-- Migration 002: Analytics views (SQLite-compatible)
-- Window functions require SQLite 3.25+ (ships with macOS 10.14+).
-- For Postgres/RDS: replace strftime('%Y',…) → EXTRACT(YEAR FROM …),
-- strftime('%Y-%m-01',…) → DATE_TRUNC('month',…), and use CREATE OR REPLACE VIEW.

DROP VIEW IF EXISTS v_genre_distribution;
CREATE VIEW v_genre_distribution AS
SELECT
    g.name                          AS genre,
    COUNT(DISTINCT st.track_id)     AS track_count
FROM saved_tracks st
JOIN track_artists ta  ON ta.track_id  = st.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres g          ON g.genre_id   = ag.genre_id
GROUP BY g.name
ORDER BY track_count DESC;


DROP VIEW IF EXISTS v_popularity_by_decade;
CREATE VIEW v_popularity_by_decade AS
SELECT
    (CAST(strftime('%Y', al.release_date) AS INTEGER) / 10 * 10) AS decade,
    ROUND(AVG(t.popularity), 1)                                   AS avg_popularity,
    COUNT(*)                                                       AS track_count
FROM saved_tracks st
JOIN tracks  t  ON t.track_id  = st.track_id
JOIN albums  al ON al.album_id = t.album_id
WHERE al.release_date IS NOT NULL
GROUP BY decade
ORDER BY decade;


DROP VIEW IF EXISTS v_top_artists;
CREATE VIEW v_top_artists AS
SELECT
    a.name,
    a.popularity                                        AS artist_popularity,
    COUNT(DISTINCT ta.track_id)                         AS track_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT ta.track_id) DESC) AS rnk
FROM saved_tracks st
JOIN track_artists ta ON ta.track_id  = st.track_id
JOIN artists       a  ON a.artist_id  = ta.artist_id
GROUP BY a.artist_id, a.name, a.popularity
ORDER BY rnk;


DROP VIEW IF EXISTS v_duration_by_genre;
CREATE VIEW v_duration_by_genre AS
SELECT
    g.name                                  AS genre,
    ROUND(AVG(t.duration_ms) / 1000.0, 1)  AS avg_duration_sec,
    COUNT(DISTINCT t.track_id)              AS track_count
FROM tracks t
JOIN track_artists ta  ON ta.track_id  = t.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres        g   ON g.genre_id   = ag.genre_id
JOIN saved_tracks  st  ON st.track_id  = t.track_id
GROUP BY g.name
HAVING COUNT(DISTINCT t.track_id) > 1
ORDER BY avg_duration_sec DESC;


DROP VIEW IF EXISTS v_explicit_ratio;
CREATE VIEW v_explicit_ratio AS
SELECT
    g.name                                                              AS genre,
    SUM(CASE WHEN t.explicit = 1 THEN 1 ELSE 0 END)                   AS explicit_count,
    SUM(CASE WHEN t.explicit = 0 THEN 1 ELSE 0 END)                   AS clean_count,
    COUNT(*)                                                            AS total,
    ROUND(SUM(CASE WHEN t.explicit = 1 THEN 1.0 ELSE 0 END)
          * 100.0 / NULLIF(COUNT(*), 0), 1)                            AS explicit_pct
FROM saved_tracks st
JOIN tracks        t   ON t.track_id   = st.track_id
JOIN track_artists ta  ON ta.track_id  = t.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres        g   ON g.genre_id   = ag.genre_id
GROUP BY g.name
HAVING COUNT(*) > 1
ORDER BY explicit_pct DESC;


DROP VIEW IF EXISTS v_tracks_over_time;
CREATE VIEW v_tracks_over_time AS
SELECT
    strftime('%Y-%m-01', added_at)  AS month,
    COUNT(*)                         AS added_this_month,
    SUM(COUNT(*)) OVER (
        ORDER BY strftime('%Y-%m-01', added_at)
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                AS running_total
FROM saved_tracks
GROUP BY strftime('%Y-%m-01', added_at)
ORDER BY month;


DROP VIEW IF EXISTS v_summary;
CREATE VIEW v_summary AS
SELECT
    (SELECT COUNT(*) FROM saved_tracks)                          AS total_tracks,
    (SELECT COUNT(DISTINCT ta.artist_id)
     FROM saved_tracks st
     JOIN track_artists ta ON ta.track_id = st.track_id)        AS total_artists,
    (SELECT COUNT(DISTINCT ag.genre_id)
     FROM saved_tracks st
     JOIN track_artists ta  ON ta.track_id  = st.track_id
     JOIN artist_genres ag  ON ag.artist_id = ta.artist_id)     AS total_genres;
