from datetime import datetime
import uuid
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    String,
    Numeric,
    Integer,
    ForeignKey,
    DateTime,
    Enum as SQLEnum,
    event,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base


class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    OVERDUE = "overdue"


class Borrower(Base):
    __tablename__ = "borrowers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    credit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    loans: Mapped[List["Loan"]] = relationship("Loan", back_populates="borrower")

    def __repr__(self) -> str:
        return f"<Borrower(id={self.id}, name='{self.name}', email='{self.email}')>"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    borrower_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("borrowers.id"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[LoanStatus] = mapped_column(
        SQLEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False
    )
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    interest_rate_apr: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disbursement_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    borrower: Mapped["Borrower"] = relationship("Borrower", back_populates="loans")
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="loan", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("amount > 0 AND amount <= 50000", name="chk_amount_range"),
        CheckConstraint("term_months > 0", name="chk_term_positive"),
        CheckConstraint("interest_rate_apr >= 0", name="chk_interest_non_negative"),
    )

    def calculate_monthly_payment(self) -> float:
        """Calculate the monthly payment amount using the loan details."""
        if self.interest_rate_apr == 0:
            return float(self.amount) / self.term_months
        
        monthly_rate = (self.interest_rate_apr / 100) / 12
        return float(
            (self.amount * monthly_rate * (1 + monthly_rate) ** self.term_months)
            / ((1 + monthly_rate) ** self.term_months - 1)
        )

    def __repr__(self) -> str:
        return f"<Loan(id={self.id}, amount={self.amount} {self.currency}, status='{self.status}')>"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    loan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    paid_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    transaction_reference: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, unique=True, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    loan: Mapped["Loan"] = relationship("Loan", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount_positive"),
        CheckConstraint(
            "(status = 'paid' AND paid_amount IS NOT NULL AND paid_at IS NOT NULL) OR "
            "(status != 'paid' AND paid_amount IS NULL AND paid_at IS NULL)",
            name="chk_payment_status_consistency",
        ),
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"


# Add indexes and other database-level optimizations
@event.listens_for(Loan, "before_insert")
def set_loan_defaults(mapper, connection, target):
    """Set default values for new loans."""
    if target.status is None:
        target.status = LoanStatus.PENDING
    if target.currency is None:
        target.currency = "USD"


@event.listens_for(Payment, "before_insert")
def set_payment_defaults(mapper, connection, target):
    """Set default values for new payments."""
    if target.status is None:
        target.status = PaymentStatus.PENDING
