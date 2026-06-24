from fastapi import APIRouter
from app.db.connection import db_cursor

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


@router.get("/revenue")
def platform_revenue():
    with db_cursor() as cur:
        cur.execute(
            "SELECT platform, model, rate_per_unit, total_units, "
            "total_revenue, revenue_rank FROM v_platform_revenue"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


@router.get("/efficiency")
def platform_efficiency():
    with db_cursor() as cur:
        cur.execute(
            "SELECT name, model, published_rate, actual_rate, "
            "total_revenue, total_units FROM v_platform_efficiency"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
