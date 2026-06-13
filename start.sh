#!/usr/bin/env bash
set -e

source .venv/bin/activate

# kill both servers on ctrl+c
trap 'kill 0' SIGINT SIGTERM

echo "==> starting api on :8000"
cd backend
uvicorn app.main:app --reload &
cd ..

echo "==> starting frontend on :5173"
cd frontend
npm run dev &
cd ..

echo ""
echo "==> open http://localhost:5173"
echo "    ctrl+c to stop both"

wait
