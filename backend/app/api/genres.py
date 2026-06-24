from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/genres", tags=["genres"])


@router.get("/revenue")
def genre_revenue():
    with db_cursor() as cur:
        cur.execute(
            "SELECT genre, total_revenue, total_units, track_count, artist_count "
            "FROM v_genre_revenue"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
