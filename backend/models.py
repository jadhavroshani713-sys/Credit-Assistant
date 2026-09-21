"""
CREDIT ASSISTANT - ORM Models

Models:
    - User          → table: users
    - CreditProfile → table: credit_profiles
    - ScoreHistory  → table: score_history
"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    """
    Represents an application user account.

    Columns
    -------
    id           : surrogate primary key
    name         : display name
    email        : unique login identifier (indexed)
    mobile       : optional phone number
    password_hash: bcrypt hash — plaintext passwords are NEVER stored
    created_at   : UTC timestamp of account creation
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    mobile: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    credit_profiles: Mapped[list["CreditProfile"]] = relationship(
        "CreditProfile",
        back_populates="user",
        lazy="select",
    )
    score_history: Mapped[list["ScoreHistory"]] = relationship(
        "ScoreHistory",
        back_populates="user",
        order_by="ScoreHistory.recorded_at",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


# ---------------------------------------------------------------------------
# CreditProfile
# ---------------------------------------------------------------------------

class CreditProfile(Base):
    """
    Stores a user's current financial and credit standing.

    One user may have multiple profile snapshots over time, but typically
    only the latest record is the active profile.

    Columns
    -------
    id               : surrogate primary key
    user_id          : FK → users.id
    credit_score     : current credit score (0 – 900)
    credit_limit     : total sanctioned credit limit
    credit_used      : amount of credit currently utilised
    utilization      : credit_used / credit_limit  (0.0 – 1.0)
    missed_payments  : number of missed EMI/bill payments
    active_loans     : count of open loan accounts
    monthly_salary   : gross monthly income
    monthly_expenses : total monthly outgoings
    debt_to_income   : monthly_expenses / monthly_salary (0.0 – 1.0)
    created_at       : UTC timestamp when record was first created
    updated_at       : UTC timestamp of the last update
    """

    __tablename__ = "credit_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Credit metrics
    credit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    credit_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    credit_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    utilization: Mapped[float | None] = mapped_column(Float, nullable=True)
    missed_payments: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    active_loans: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

    # Financial metrics
    monthly_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_expenses: Mapped[float | None] = mapped_column(Float, nullable=True)
    debt_to_income: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user: Mapped["User"] = relationship("User", back_populates="credit_profiles")

    def __repr__(self) -> str:
        return (
            f"<CreditProfile id={self.id} user_id={self.user_id} "
            f"score={self.credit_score}>"
        )


# ---------------------------------------------------------------------------
# ScoreHistory
# ---------------------------------------------------------------------------

class ScoreHistory(Base):
    """
    Immutable audit log of credit-score changes for a user.

    Each row records a transition from old_score → new_score at a given
    point in time.  Rows are never updated; only new rows are inserted.

    Columns
    -------
    id          : surrogate primary key
    user_id     : FK → users.id
    old_score   : credit score before the change
    new_score   : credit score after the change
    improvement : new_score - old_score  (negative = decline)
    recorded_at : UTC timestamp of the recorded change
    """

    __tablename__ = "score_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_score: Mapped[int] = mapped_column(Integer, nullable=False)
    improvement: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user: Mapped["User"] = relationship("User", back_populates="score_history")

    def __repr__(self) -> str:
        return (
            f"<ScoreHistory id={self.id} user_id={self.user_id} "
            f"{self.old_score} -> {self.new_score}>"
        )


# ---------------------------------------------------------------------------
# Export surface
# ---------------------------------------------------------------------------
__all__ = ["User", "CreditProfile", "ScoreHistory", "Base"]
