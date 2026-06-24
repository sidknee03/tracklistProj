from fastapi import APIRouter
from app.db.connection import db_cursor, PH

router = APIRouter(prefix="/api/artists", tags=["artists"])


@router.get("/top")
def top_artists(limit: int = 15):
    with db_cursor() as cur:
        cur.execute(
            f"SELECT name, country, monthly_listeners, total_revenue, total_units, rnk "
            f"FROM v_artist_earnings LIMIT {PH}",
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
