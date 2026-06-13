# Music Analytics Dashboard

SQL-backed music analytics dashboard. Pulls your Spotify library, models it in PostgreSQL, and serves it through a FastAPI + React frontend.

## Stack

| Layer | Tech |
|---|---|
| Database | PostgreSQL 16 |
| Ingestion | Python + Spotipy |
| API | FastAPI + psycopg2 |
| Frontend | React + Recharts (Vite) |
| Local infra | Docker Compose |
| Tests / CI | pytest + GitHub Actions |
| Deploy | AWS RDS + ECS Fargate + Terraform |

## Quick start (local)

```bash
# 1. Copy env
cp .env.example .env
# Fill in SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET in .env

# 2. Start Postgres
docker compose up db -d

# 3. Fetch your Spotify data  (opens browser for OAuth)
cd ingestion
pip install -r requirements.txt
python spotify_fetch.py

# ─── Fallback: load from Kaggle CSV instead ───
# python csv_fallback.py --csv path/to/tracks.csv

# 4. Run migrations + load data into Postgres
python loader.py

# 5. Start the API
cd ../backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 6. Start the frontend (new terminal)
cd ../frontend
npm install
npm run dev
# → http://localhost:5173
```

## Spotify setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app.
2. Set the Redirect URI to `http://localhost:8888/callback`.
3. Copy Client ID and Client Secret into `.env`.

## Docker Compose (API + DB)

```bash
docker compose up --build
# API  → http://localhost:8000
# Docs → http://localhost:8000/docs
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/stats/summary` | Total tracks, artists, genres |
| GET | `/api/genres/distribution` | Track count per genre |
| GET | `/api/popularity/by-decade` | Avg popularity bucketed by decade |
| GET | `/api/artists/top` | Top artists ranked with RANK() window fn |
| GET | `/api/duration/by-genre` | Avg track duration per genre |

## Database schema

```
artists ──< artist_genres >── genres
   │
   └──< track_artists >── tracks ──> albums
                               │
                               └──< saved_tracks
```

## Analytics SQL (as views)

| View | SQL features |
|---|---|
| `v_genre_distribution` | 4-table join |
| `v_popularity_by_decade` | EXTRACT + GROUP BY |
| `v_top_artists` | RANK() OVER window function |
| `v_duration_by_genre` | 4-table join + AVG |
| `v_explicit_ratio` | FILTER aggregate |
| `v_tracks_over_time` | SUM() OVER running total |

## Tests

```bash
cd backend
pytest -v
```

## Deploy to AWS

```bash
# 1. Configure AWS CLI and Terraform
cd infra/aws
terraform init
terraform apply -var="db_password=yourpassword" -var="ecr_image_uri=placeholder"

# 2. Build + push image + update ECS service
cd ../..
./infra/aws/deploy.sh

# 3. Update DATABASE_URL in your ECS task to point at the RDS endpoint
terraform output rds_endpoint
```

## Screenshots

> Add a screenshot of the running dashboard here after first deploy.
