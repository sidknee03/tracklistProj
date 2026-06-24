from fastapi import APIRouter, HTTPException
from app.db.connection import db_cursor

router = APIRouter(prefix="/api", tags=["summary"])


@router.get("/summary")
def get_summary():
    with db_cursor() as cur:
        cur.execute(
            "SELECT total_artists, total_tracks, total_platforms, "
            "total_revenue_usd, total_streams FROM v_summary"
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No data loaded — run seed.py first")
    return dict(row)
