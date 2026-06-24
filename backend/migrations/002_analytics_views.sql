-- Migration 002: Analytics views (SQLite-compatible, window functions need SQLite 3.25+)
-- For Postgres: replace strftime → EXTRACT/DATE_TRUNC, DROP+CREATE → CREATE OR REPLACE VIEW

-- Dashboard summary
DROP VIEW IF EXISTS v_summary;
CREATE VIEW v_summary AS
SELECT
    (SELECT COUNT(DISTINCT artist_id) FROM artists)        AS total_artists,
    (SELECT COUNT(*)                  FROM tracks)          AS total_tracks,
    (SELECT COUNT(*)                  FROM platforms)       AS total_platforms,
    (SELECT ROUND(SUM(revenue), 2)    FROM streams)         AS total_revenue_usd,
    (SELECT SUM(units)
     FROM streams s JOIN platforms p ON p.platform_id = s.platform_id
     WHERE p.model = 'stream')                              AS total_streams;


-- Revenue + volume per platform, ranked — good for: "which platform pays most?"
DROP VIEW IF EXISTS v_platform_revenue;
CREATE VIEW v_platform_revenue AS
SELECT
    p.name                                  AS platform,
    p.model,
    p.rate_per_unit,
    SUM(s.units)                            AS total_units,
    ROUND(SUM(s.revenue), 2)               AS total_revenue,
    RANK() OVER (ORDER BY SUM(s.revenue) DESC) AS revenue_rank
FROM streams s
JOIN platforms p ON p.platform_id = s.platform_id
GROUP BY p.platform_id, p.name, p.model, p.rate_per_unit
ORDER BY revenue_rank;


-- Top artists by total earnings across all platforms (3-table join + window fn)
DROP VIEW IF EXISTS v_artist_earnings;
CREATE VIEW v_artist_earnings AS
SELECT
    a.name,
    a.country,
    a.monthly_listeners,
    ROUND(SUM(s.revenue), 2)                           AS total_revenue,
    SUM(s.units)                                        AS total_units,
    RANK() OVER (ORDER BY SUM(s.revenue) DESC)          AS rnk
FROM streams s
JOIN tracks  t ON t.track_id  = s.track_id
JOIN artists a ON a.artist_id = t.artist_id
GROUP BY a.artist_id, a.name, a.country, a.monthly_listeners
ORDER BY rnk;


-- Revenue by genre across all platforms (4-table join)
DROP VIEW IF EXISTS v_genre_revenue;
CREATE VIEW v_genre_revenue AS
SELECT
    g.name                      AS genre,
    ROUND(SUM(s.revenue), 2)   AS total_revenue,
    SUM(s.units)                AS total_units,
    COUNT(DISTINCT t.track_id)  AS track_count,
    COUNT(DISTINCT t.artist_id) AS artist_count
FROM streams     s
JOIN tracks      t  ON t.track_id  = s.track_id
JOIN artist_genres ag ON ag.artist_id = t.artist_id
JOIN genres      g  ON g.genre_id  = ag.genre_id
GROUP BY g.name
ORDER BY total_revenue DESC;


-- Monthly revenue with running total window function
DROP VIEW IF EXISTS v_monthly_revenue;
CREATE VIEW v_monthly_revenue AS
SELECT
    period,
    ROUND(SUM(revenue), 2)  AS monthly_revenue,
    SUM(SUM(revenue)) OVER (
        ORDER BY period
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                        AS running_total
FROM streams
GROUP BY period
ORDER BY period;


-- Platform efficiency: actual revenue per unit vs published rate
DROP VIEW IF EXISTS v_platform_efficiency;
CREATE VIEW v_platform_efficiency AS
SELECT
    p.name,
    p.model,
    ROUND(p.rate_per_unit, 4)                                           AS published_rate,
    ROUND(SUM(s.revenue) * 1.0 / NULLIF(SUM(s.units), 0), 6)          AS actual_rate,
    ROUND(SUM(s.revenue), 2)                                            AS total_revenue,
    SUM(s.units)                                                         AS total_units
FROM streams s
JOIN platforms p ON p.platform_id = s.platform_id
GROUP BY p.platform_id, p.name, p.model, p.rate_per_unit
ORDER BY total_revenue DESC;
