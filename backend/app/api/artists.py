from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/artists", tags=["artists"])


@router.get("/top")
def top_artists(limit: int = 15):
    with db_cursor() as cur:
        cur.execute(
            "SELECT name, artist_popularity, track_count, rnk FROM v_top_artists LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
