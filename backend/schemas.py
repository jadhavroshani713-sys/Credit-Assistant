"""
CREDIT ASSISTANT - Pydantic Schemas
Phase 5: Request, response, and AI recommendation schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth — Registration
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Incoming payload for POST /register."""

    name: str = Field(..., min_length=1, max_length=100, examples=["Jane Doe"])
    email: EmailStr = Field(..., examples=["jane@example.com"])
    mobile: Optional[str] = Field(
        default=None, max_length=20, examples=["9876543210"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass123"],
        description="Must be at least 8 characters.",
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank.")
        return v.strip()


class RegisterResponse(BaseModel):
    """Safe user payload returned after successful registration.
    Never includes password or password_hash."""

    id: int
    name: str
    email: str
    mobile: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Auth — Login
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Incoming payload for POST /login."""

    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(..., min_length=1, examples=["SecurePass123"])


class LoginResponse(BaseModel):
    """Response returned after a successful login.
    Never includes password or password_hash."""

    message: str
    user_id: int
    name: str
    email: str


# ---------------------------------------------------------------------------
# Financial Data
# ---------------------------------------------------------------------------

class FinancialDataRequest(BaseModel):
    """Incoming payload for POST /financial-data.

    Server recalculates utilization and debt_to_income — never trust
    client-supplied derived values.
    """

    user_id: int = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=900, examples=[720])
    credit_limit: float = Field(..., ge=0, examples=[100000.0])
    credit_used: float = Field(..., ge=0, examples=[35000.0])
    missed_payments: int = Field(..., ge=0, examples=[0])
    active_loans: int = Field(..., ge=0, examples=[2])
    monthly_salary: float = Field(..., ge=0, examples=[60000.0])
    monthly_expenses: float = Field(..., ge=0, examples=[25000.0])


class FinancialDataResponse(BaseModel):
    """Response after saving financial data."""

    message: str
    profile_id: int
    user_id: int
    credit_score: int
    credit_limit: float
    credit_used: float
    utilization_pct: float          # percentage, e.g. 35.0 for 35%
    missed_payments: int
    active_loans: int
    monthly_salary: float
    monthly_expenses: float
    debt_to_income_pct: float       # percentage, e.g. 41.67
    score_improvement: Optional[int]   # null for first-ever submission


# ---------------------------------------------------------------------------
# Score History
# ---------------------------------------------------------------------------

class ScoreHistoryEntry(BaseModel):
    """A single score change record."""

    id: int
    old_score: Optional[int]
    new_score: int
    improvement: Optional[int]
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardUserInfo(BaseModel):
    id: int
    name: str
    email: str
    mobile: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardProfileInfo(BaseModel):
    id: int
    credit_score: Optional[int]
    credit_limit: Optional[float]
    credit_used: Optional[float]
    utilization: Optional[float]          # stored as percentage
    missed_payments: Optional[int]
    active_loans: Optional[int]
    monthly_salary: Optional[float]
    monthly_expenses: Optional[float]
    debt_to_income: Optional[float]       # stored as percentage
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    """Full dashboard payload returned by GET /dashboard/{user_id}."""

    user: DashboardUserInfo
    profile: Optional[DashboardProfileInfo]   # None if no financial data yet
    score_history: list[ScoreHistoryEntry]
    has_financial_data: bool


# ---------------------------------------------------------------------------
# AI Recommendations
# ---------------------------------------------------------------------------

class RecommendationResponse(BaseModel):
    """Structured AI recommendations payload returned by GET /recommendations/{user_id}."""

    overall_assessment: str
    critical_issues: list[str]
    recommendations: list[str]
    improvement_guidance: str

