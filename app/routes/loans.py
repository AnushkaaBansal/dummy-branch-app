from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
from typing import List

from ..db import SessionContext, get_db
from ..models import Loan
from ..schemas import CreateLoanRequest, LoanOut

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[LoanOut])
async def list_loans(db: SessionContext = Depends(get_db)):
    result = db.execute(select(Loan).order_by(Loan.created_at.desc()))
    loans = [
        LoanOut.model_validate(obj, from_attributes=True)
        for obj in result.scalars().all()
    ]
    return loans

@router.get("/{loan_id}", response_model=LoanOut)
async def get_loan(loan_id: UUID, db: SessionContext = Depends(get_db)):
    loan = db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return LoanOut.model_validate(loan, from_attributes=True)

@router.post("/", response_model=LoanOut, status_code=201)
async def create_loan(loan_data: CreateLoanRequest, db: SessionContext = Depends(get_db)):
    loan = Loan(
        borrower_id=loan_data.borrower_id,
        amount=Decimal(str(loan_data.amount)),
        currency=loan_data.currency.upper(),
        term_months=loan_data.term_months,
        interest_rate_apr=(Decimal(str(loan_data.interest_rate_apr)) if loan_data.interest_rate_apr is not None else None),
        status="pending",
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return LoanOut.model_validate(loan, from_attributes=True)
