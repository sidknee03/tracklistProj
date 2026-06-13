from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/popularity", tags=["popularity"])


@router.get("/by-decade")
def popularity_by_decade():
    with db_cursor() as cur:
        cur.execute(
            "SELECT decade, avg_popularity, track_count FROM v_popularity_by_decade"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
