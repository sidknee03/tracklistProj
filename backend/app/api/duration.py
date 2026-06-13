from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/duration", tags=["duration"])


@router.get("/by-genre")
def duration_by_genre(limit: int = 15):
    with db_cursor() as cur:
        cur.execute(
            "SELECT genre, avg_duration_sec, track_count FROM v_duration_by_genre LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
