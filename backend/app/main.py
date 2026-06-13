from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import stats, genres, popularity, artists, duration

app = FastAPI(title="Music Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

for router in (stats.router, genres.router, popularity.router, artists.router, duration.router):
    app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
