#!/usr/bin/env bash
set -e

echo "==> setting up royalty.db"

# python venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "==> created .venv"
fi
source .venv/bin/activate
pip install -q -r ingestion/requirements.txt
pip install -q -r backend/requirements.txt
echo "==> python deps ready"

# frontend
if [ ! -d "frontend/node_modules" ]; then
  cd frontend && npm install --silent && cd ..
  echo "==> node deps ready"
fi

# seed the database (no credentials needed)
echo "==> seeding database..."
cd ingestion
python3 seed.py
cd ..

echo ""
echo "==> done. run ./start.sh to launch"
