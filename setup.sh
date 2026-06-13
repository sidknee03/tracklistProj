#!/usr/bin/env bash
set -e

echo "==> setting up tracklist"

# 1. python venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "==> created .venv"
fi
source .venv/bin/activate
pip install -q -r ingestion/requirements.txt
pip install -q -r backend/requirements.txt
echo "==> python deps ready"

# 2. frontend
if [ ! -d "frontend/node_modules" ]; then
  cd frontend && npm install --silent && cd ..
  echo "==> node deps ready"
fi

# 3. .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "!! .env created — fill in your Spotify credentials before continuing:"
  echo "   SPOTIFY_CLIENT_ID"
  echo "   SPOTIFY_CLIENT_SECRET"
  echo ""
  echo "   get them at: developer.spotify.com/dashboard"
  exit 0
fi

# 4. fetch + load
source .venv/bin/activate
cd ingestion
python3 spotify_fetch.py
python3 loader.py
cd ..

echo ""
echo "==> done. run ./start.sh to launch"
