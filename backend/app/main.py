from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import summary, platforms, artists, genres, trends

app = FastAPI(title="Streaming Royalty Analytics API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

for router in (summary.router, platforms.router, artists.router, genres.router, trends.router):
    app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
