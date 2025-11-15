from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from typing import Dict, Any

from ..db import SessionContext, get_db
from ..models import Loan

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
async def get_stats(db: SessionContext = Depends(get_db)) -> Dict[str, Any]:
    total_count = db.execute(select(func.count(Loan.id))).scalar_one()
    total_amount = db.execute(select(func.coalesce(func.sum(Loan.amount), 0))).scalar_one()
    avg_amount = db.execute(select(func.coalesce(func.avg(Loan.amount), 0))).scalar_one()

    by_status_rows = db.execute(select(Loan.status, func.count(Loan.id)).group_by(Loan.status)).all()
    by_currency_rows = db.execute(select(Loan.currency, func.count(Loan.id)).group_by(Loan.currency)).all()

    by_status = {k: v for k, v in by_status_rows}
    by_currency = {k: v for k, v in by_currency_rows}

    return {
        "total_loans": int(total_count),
        "total_amount": float(total_amount),
        "avg_amount": float(avg_amount),
        "by_status": by_status,
        "by_currency": by_currency,
    }
