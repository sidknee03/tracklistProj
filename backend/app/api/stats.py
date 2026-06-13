from fastapi import APIRouter, HTTPException
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
def get_summary():
    with db_cursor() as cur:
        cur.execute("SELECT total_tracks, total_artists, total_genres FROM v_summary")
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No data loaded yet")
    return dict(row)
