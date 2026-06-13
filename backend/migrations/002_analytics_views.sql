-- Migration 002: Analytics views
-- Each view corresponds to one API endpoint.
-- At least 2 join across 3+ tables, at least 2 use window functions.

-- View 1: Genre distribution across the library
-- Joins: saved_tracks -> track_artists -> artist_genres -> genres  (4 tables)
CREATE OR REPLACE VIEW v_genre_distribution AS
SELECT
    g.name                    AS genre,
    COUNT(DISTINCT st.track_id) AS track_count
FROM saved_tracks st
JOIN track_artists ta  ON ta.track_id  = st.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres g          ON g.genre_id   = ag.genre_id
GROUP BY g.name
ORDER BY track_count DESC;


-- View 2: Average popularity by release decade
-- Joins: saved_tracks -> tracks -> albums  (3 tables)
CREATE OR REPLACE VIEW v_popularity_by_decade AS
SELECT
    (EXTRACT(YEAR FROM al.release_date) / 10 * 10)::INTEGER AS decade,
    ROUND(AVG(t.popularity), 1)                             AS avg_popularity,
    COUNT(*)                                                 AS track_count
FROM saved_tracks st
JOIN tracks  t  ON t.track_id  = st.track_id
JOIN albums  al ON al.album_id = t.album_id
WHERE al.release_date IS NOT NULL
GROUP BY decade
ORDER BY decade;


-- View 3: Top artists by track count with RANK window function
-- Joins: saved_tracks -> track_artists -> artists  (3 tables)
CREATE OR REPLACE VIEW v_top_artists AS
SELECT
    a.name,
    a.popularity                                       AS artist_popularity,
    COUNT(DISTINCT ta.track_id)                        AS track_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT ta.track_id) DESC) AS rnk
FROM saved_tracks st
JOIN track_artists ta ON ta.track_id  = st.track_id
JOIN artists       a  ON a.artist_id  = ta.artist_id
GROUP BY a.artist_id, a.name, a.popularity
ORDER BY rnk;


-- View 4: Average track duration by genre
-- Joins: tracks -> track_artists -> artist_genres -> genres  (4 tables)
CREATE OR REPLACE VIEW v_duration_by_genre AS
SELECT
    g.name                              AS genre,
    ROUND(AVG(t.duration_ms) / 1000.0, 1) AS avg_duration_sec,
    COUNT(DISTINCT t.track_id)          AS track_count
FROM tracks t
JOIN track_artists ta  ON ta.track_id  = t.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres g          ON g.genre_id   = ag.genre_id
JOIN saved_tracks st   ON st.track_id  = t.track_id
GROUP BY g.name
HAVING COUNT(DISTINCT t.track_id) > 1
ORDER BY avg_duration_sec DESC;


-- View 5: Explicit vs clean ratio per genre
CREATE OR REPLACE VIEW v_explicit_ratio AS
SELECT
    g.name                                                  AS genre,
    COUNT(*) FILTER (WHERE t.explicit = TRUE)               AS explicit_count,
    COUNT(*) FILTER (WHERE t.explicit = FALSE)              AS clean_count,
    COUNT(*)                                                AS total,
    ROUND(
        COUNT(*) FILTER (WHERE t.explicit = TRUE) * 100.0 / NULLIF(COUNT(*), 0),
        1
    )                                                       AS explicit_pct
FROM saved_tracks st
JOIN tracks        t   ON t.track_id   = st.track_id
JOIN track_artists ta  ON ta.track_id  = t.track_id
JOIN artist_genres ag  ON ag.artist_id = ta.artist_id
JOIN genres        g   ON g.genre_id   = ag.genre_id
GROUP BY g.name
HAVING COUNT(*) > 1
ORDER BY explicit_pct DESC;


-- View 6: Running total of tracks added over time (window function)
CREATE OR REPLACE VIEW v_tracks_over_time AS
SELECT
    DATE_TRUNC('month', added_at)::DATE AS month,
    COUNT(*)                            AS added_this_month,
    SUM(COUNT(*)) OVER (
        ORDER BY DATE_TRUNC('month', added_at)
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                   AS running_total
FROM saved_tracks
GROUP BY DATE_TRUNC('month', added_at)
ORDER BY month;


-- Summary stats view (used by /api/stats/summary)
CREATE OR REPLACE VIEW v_summary AS
SELECT
    (SELECT COUNT(*) FROM saved_tracks)   AS total_tracks,
    (SELECT COUNT(DISTINCT ta.artist_id)
     FROM saved_tracks st
     JOIN track_artists ta ON ta.track_id = st.track_id) AS total_artists,
    (SELECT COUNT(DISTINCT ag.genre_id)
     FROM saved_tracks st
     JOIN track_artists ta  ON ta.track_id  = st.track_id
     JOIN artist_genres ag  ON ag.artist_id = ta.artist_id) AS total_genres;
