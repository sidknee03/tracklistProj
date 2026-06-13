from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/genres", tags=["genres"])


@router.get("/distribution")
def genre_distribution(limit: int = 20):
    with db_cursor() as cur:
        cur.execute(
            "SELECT genre, track_count FROM v_genre_distribution LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
