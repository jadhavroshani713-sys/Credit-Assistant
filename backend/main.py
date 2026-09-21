"""
CREDIT ASSISTANT - Backend API
Phase 5: Authentication, Core Routes & Gemini AI Recommendations

Endpoints
---------
GET  /                          Root / phase info
GET  /health                    Health check
POST /register                  Create a new user account
POST /login                     Authenticate an existing user
POST /financial-data            Submit / update financial profile
GET  /dashboard/{user_id}       Retrieve full user dashboard data
GET  /recommendations/{user_id} Retrieve AI credit recommendations
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# ---- project imports (order matters: env first, then DB, then models) ----
load_dotenv()

from database import engine, Base, get_db
import models                          # noqa: F401 — register tables with Base
from models import CreditProfile, ScoreHistory, User
from schemas import (
    DashboardResponse,
    DashboardProfileInfo,
    DashboardUserInfo,
    FinancialDataRequest,
    FinancialDataResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ScoreHistoryEntry,
    RecommendationResponse,
)
from security import hash_password, verify_password
from ai import get_recommendations_from_gemini

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed CORS origins (read from env for easy overrides)
# ---------------------------------------------------------------------------
_CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")
    if origin.strip()
]

# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables on startup (idempotent, safe for dev)."""
    Base.metadata.create_all(bind=engine)
    logger.info("[startup] Database tables verified / created.")
    yield
    logger.info("[shutdown] Application stopped.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Credit Assistant API",
    description=(
        "AI-powered Credit Assistant backend.  "
        "Phase 5: Gemini AI & Frontend Integration."
    ),
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Convenience type alias for the DB dependency
DbDep = Annotated[Session, Depends(get_db)]


# ===========================================================================
# Utility routes
# ===========================================================================

@app.get("/", tags=["Status"], summary="Root — phase info")
def read_root():
    """Returns project name and current phase."""
    return {
        "project": "Credit Assistant",
        "phase": "Phase 5 - Gemini AI & Frontend Integration",
        "status": "ok",
    }


@app.get("/health", tags=["Status"], summary="Health check")
def health_check():
    """Returns {'status': 'ok'} when the server is running."""
    return {"status": "ok"}


# ===========================================================================
# POST /register
# ===========================================================================

@app.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Register a new user account",
)
def register(payload: RegisterRequest, db: DbDep):
    """
    Create a new user account.

    - Validates name, email, mobile, password.
    - Rejects duplicate email addresses (HTTP 409).
    - Hashes the password with bcrypt before storage.
    - Never returns password or password_hash.
    """
    # --- duplicate email check ---
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    # --- create user ---
    user = User(
        name=payload.name.strip(),
        email=payload.email,
        mobile=payload.mobile,
        password_hash=hash_password(payload.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as exc:
        db.rollback()
        logger.error("Registration DB error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user. Please try again.",
        )

    logger.info("New user registered: id=%s email=%s", user.id, user.email)
    return user


# ===========================================================================
# POST /login
# ===========================================================================

@app.post(
    "/login",
    response_model=LoginResponse,
    tags=["Authentication"],
    summary="Log in with email and password",
)
def login(payload: LoginRequest, db: DbDep):
    """
    Authenticate a user.

    - Looks up the user by email.
    - Verifies the supplied password against the stored bcrypt hash.
    - Returns HTTP 401 for any credential mismatch (deliberately vague
      to avoid user-enumeration attacks).
    - Never returns password or password_hash.
    """
    # --- look up user ---
    user = db.query(User).filter(User.email == payload.email).first()

    # --- constant-time-safe check (bcrypt verify even on missing user) ---
    _DUMMY_HASH = "$2b$12$invalidhashpadding000000000000000000000000000000000000000"
    stored_hash = user.password_hash if user else _DUMMY_HASH

    if not user or not verify_password(payload.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    logger.info("User logged in: id=%s email=%s", user.id, user.email)
    return LoginResponse(
        message="Login successful.",
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


# ===========================================================================
# POST /financial-data
# ===========================================================================

@app.post(
    "/financial-data",
    response_model=FinancialDataResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Financial"],
    summary="Submit or update a user's financial profile",
)
def submit_financial_data(payload: FinancialDataRequest, db: DbDep):
    """
    Save a new financial profile snapshot for an existing user.

    Server-side calculations
    ------------------------
    - **utilization** = (credit_used / credit_limit) * 100
      Stored as a percentage (0–100+).
      Returns 0.0 when credit_limit is zero.

    - **debt_to_income** = (monthly_expenses / monthly_salary) * 100
      Stored as a percentage.
      Returns 0.0 when monthly_salary is zero.

    Score history
    -------------
    - Finds the user's most recent ScoreHistory row.
    - Records old_score → new_score transition.
    - improvement = new_score - old_score (can be negative).
    - For a user's first submission, old_score is None.
    """
    # --- verify user exists ---
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={payload.user_id} not found.",
        )

    # --- server-side derived calculations ---
    if payload.credit_limit > 0:
        utilization = round((payload.credit_used / payload.credit_limit) * 100, 2)
    else:
        utilization = 0.0
        logger.warning(
            "user_id=%s submitted credit_limit=0; utilization set to 0.",
            payload.user_id,
        )

    if payload.monthly_salary > 0:
        dti = round((payload.monthly_expenses / payload.monthly_salary) * 100, 2)
    else:
        dti = 0.0
        logger.warning(
            "user_id=%s submitted monthly_salary=0; debt_to_income set to 0.",
            payload.user_id,
        )

    # --- score history ---
    previous_entry = (
        db.query(ScoreHistory)
        .filter(ScoreHistory.user_id == payload.user_id)
        .order_by(ScoreHistory.recorded_at.desc())
        .first()
    )
    old_score = previous_entry.new_score if previous_entry else None
    improvement = (payload.credit_score - old_score) if old_score is not None else None

    try:
        # Create CreditProfile snapshot
        profile = CreditProfile(
            user_id=payload.user_id,
            credit_score=payload.credit_score,
            credit_limit=payload.credit_limit,
            credit_used=payload.credit_used,
            utilization=utilization,
            missed_payments=payload.missed_payments,
            active_loans=payload.active_loans,
            monthly_salary=payload.monthly_salary,
            monthly_expenses=payload.monthly_expenses,
            debt_to_income=dti,
        )
        db.add(profile)

        # Create ScoreHistory entry
        history_entry = ScoreHistory(
            user_id=payload.user_id,
            old_score=old_score,
            new_score=payload.credit_score,
            improvement=improvement,
        )
        db.add(history_entry)

        db.commit()
        db.refresh(profile)

    except Exception as exc:
        db.rollback()
        logger.error("Financial data DB error for user_id=%s: %s", payload.user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save financial data. Please try again.",
        )

    logger.info(
        "Financial data saved: user_id=%s profile_id=%s score=%s util=%.2f%% dti=%.2f%%",
        payload.user_id, profile.id, payload.credit_score, utilization, dti,
    )
    return FinancialDataResponse(
        message="Financial profile saved successfully.",
        profile_id=profile.id,
        user_id=payload.user_id,
        credit_score=payload.credit_score,
        credit_limit=payload.credit_limit,
        credit_used=payload.credit_used,
        utilization_pct=utilization,
        missed_payments=payload.missed_payments,
        active_loans=payload.active_loans,
        monthly_salary=payload.monthly_salary,
        monthly_expenses=payload.monthly_expenses,
        debt_to_income_pct=dti,
        score_improvement=improvement,
    )


# ===========================================================================
# GET /dashboard/{user_id}
# ===========================================================================

@app.get(
    "/dashboard/{user_id}",
    response_model=DashboardResponse,
    tags=["Dashboard"],
    summary="Retrieve a user's full dashboard data",
)
def get_dashboard(user_id: int, db: DbDep):
    """
    Return the full dashboard payload for a given user.

    Includes
    --------
    - User info (no password / hash)
    - Latest CreditProfile snapshot (if any)
    - Full ScoreHistory list (chronological)

    Returns HTTP 404 if user_id does not exist.
    Returns a valid response with profile=None when no financial data
    has been submitted yet.
    """
    # --- user ---
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    # --- latest credit profile ---
    latest_profile = (
        db.query(CreditProfile)
        .filter(CreditProfile.user_id == user_id)
        .order_by(CreditProfile.updated_at.desc())
        .first()
    )

    # --- score history (chronological) ---
    history = (
        db.query(ScoreHistory)
        .filter(ScoreHistory.user_id == user_id)
        .order_by(ScoreHistory.recorded_at.asc())
        .all()
    )

    profile_data = DashboardProfileInfo.model_validate(latest_profile) if latest_profile else None
    history_data = [ScoreHistoryEntry.model_validate(h) for h in history]

    return DashboardResponse(
        user=DashboardUserInfo.model_validate(user),
        profile=profile_data,
        score_history=history_data,
        has_financial_data=latest_profile is not None,
    )


# ===========================================================================
# GET /recommendations/{user_id}
# ===========================================================================

@app.get(
    "/recommendations/{user_id}",
    response_model=RecommendationResponse,
    tags=["AI Recommendations"],
    summary="Retrieve AI-powered credit recommendations for a user",
)
def get_recommendations(user_id: int, db: DbDep):
    """
    Generate tailored credit health guidance for a user using Google Gemini.

    - Verifies user exists (HTTP 404 if missing)
    - Retrieves latest CreditProfile (HTTP 404 if no profile exists)
    - Sends structured prompt to Gemini with Indian credit context
    - Returns structured JSON recommendations or professional fallback
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    latest_profile = (
        db.query(CreditProfile)
        .filter(CreditProfile.user_id == user_id)
        .order_by(CreditProfile.updated_at.desc())
        .first()
    )

    if not latest_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial profile found for this user. Please submit financial data first.",
        )

    result = get_recommendations_from_gemini(latest_profile, user_name=user.name)
    return RecommendationResponse(**result)

