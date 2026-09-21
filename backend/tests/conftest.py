"""
CREDIT ASSISTANT - Test Configuration (Phase 4)

Uses SQLite :memory: with StaticPool so every connection in the test
shares the same in-memory database (avoiding the "no such table" issue
that occurs because normally each :memory: connection is a separate DB).
"""
import sys
import os

# Make backend package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool   # <-- key fix


# ---------------------------------------------------------------------------
# Shared in-memory engine — StaticPool forces all connections to reuse
# the same underlying sqlite3 connection, so tables created by create_all
# are visible to every query in the same test.
# ---------------------------------------------------------------------------
def _make_test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    return engine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def client():
    """
    Provide a FastAPI TestClient backed by a fresh in-memory SQLite DB.

    1. Creates a new engine + session for this test.
    2. Creates all tables.
    3. Overrides get_db so routes use the test session.
    4. Tears down after the test.
    """
    from main import app
    from database import get_db, Base
    import models  # noqa — registers User, CreditProfile, ScoreHistory with Base

    engine = _make_test_engine()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables in the shared in-memory DB
    Base.metadata.create_all(bind=engine)

    session = Session()

    def override_get_db():
        try:
            yield session
        finally:
            pass  # closed in teardown below

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    # Teardown
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    app.dependency_overrides.clear()
