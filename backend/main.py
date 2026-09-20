"""
CREDIT ASSISTANT - Backend
Phase 2: Database Schema & Models
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables before importing database / models
load_dotenv()

from database import engine, Base

# Import ALL models so SQLAlchemy's metadata knows about every table
# before Base.metadata.create_all() is called.
import models  # noqa: F401  (User, CreditProfile, ScoreHistory)


# ---------------------------------------------------------------------------
# Application lifespan — runs once on startup and once on shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup (development convenience)."""
    Base.metadata.create_all(bind=engine)
    print("[startup] Database tables verified / created.")
    yield
    # Nothing to tear down in Phase 2
    print("[shutdown] Application stopped.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Credit Assistant API",
    description="AI-powered Credit Assistant backend",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS — allow local dev frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "project": "Credit Assistant",
        "phase": "Phase 2 - Database Schema",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
