from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/monthly")
def monthly_revenue():
    with db_cursor() as cur:
        cur.execute("SELECT period, monthly_revenue, running_total FROM v_monthly_revenue")
        rows = cur.fetchall()
    return [dict(r) for r in rows]
