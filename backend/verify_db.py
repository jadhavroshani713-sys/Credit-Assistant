"""
CREDIT ASSISTANT - Phase 2 Database Verification Script
Run from the project root:
Run from the project root:
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from database import engine, Base
import models  # noqa: F401 -- registers User, CreditProfile, ScoreHistory


EXPECTED_TABLES = {
    "users": {
        "id", "name", "email", "mobile", "password_hash", "created_at"
    },
    "credit_profiles": {
        "id", "user_id", "credit_score", "credit_limit", "credit_used",
        "utilization", "missed_payments", "active_loans",
        "monthly_salary", "monthly_expenses", "debt_to_income",
        "created_at", "updated_at",
    },
    "score_history": {
        "id", "user_id", "old_score", "new_score", "improvement", "recorded_at"
    },
}

_results = []


def sep(char="-", w=60):
    print(char * w)


def check(label, passed, detail=""):
    icon = "[PASS]" if passed else "[FAIL]"
    line = f"  {icon}  {label}"
    if detail:
        line += f"\n         >> {detail}"
    print(line)
    _results.append(passed)
    return passed


def run():
    sep("=")
    print("  CREDIT ASSISTANT -- Phase 2 Database Verification")
    sep("=")

    # 1. Connection
    print("\n[1] Database connection")
    sep()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        check("Connection established", True, str(engine.url))
    except Exception as exc:
        check("Connection established", False, str(exc))

    # 2. Table creation
    print("\n[2] Table creation (create_all)")
    sep()
    try:
        Base.metadata.create_all(bind=engine)
        check("Base.metadata.create_all() succeeded", True)
    except Exception as exc:
        check("Base.metadata.create_all() succeeded", False, str(exc))

    # 3. Tables + columns
    print("\n[3] Table existence and columns")
    sep()
    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())

    for tbl, expected_cols in EXPECTED_TABLES.items():
        if not check(f"Table '{tbl}' exists", tbl in actual_tables):
            continue
        actual_cols = {c["name"] for c in inspector.get_columns(tbl)}
        missing = expected_cols - actual_cols
        check(
            f"  All columns in '{tbl}'",
            not missing,
            f"missing: {sorted(missing)}" if missing else "",
        )

    # 4. Foreign keys
    print("\n[4] Foreign key constraints")
    sep()
    fk_pairs = [
        ("credit_profiles", "user_id", "users"),
        ("score_history",   "user_id", "users"),
    ]
    for src, col, ref in fk_pairs:
        fks = inspector.get_foreign_keys(src)
        found = any(
            fk.get("referred_table") == ref and col in fk.get("constrained_columns", [])
            for fk in fks
        )
        check(f"FK {src}.{col} -> {ref}.id", found)

    # 5. Session round-trip (rolled back -- no permanent data)
    print("\n[5] Session round-trip (insert / read / rollback)")
    sep()
    from models import User
    try:
        with Session(engine) as session:
            tmp = User(
                name="__verify__",
                email="__verify__@test.local",
                password_hash="__not_real__",
            )
            session.add(tmp)
            session.flush()
            fetched = session.get(User, tmp.id)
            assert fetched is not None
            assert fetched.email == "__verify__@test.local"
            session.rollback()
        check("Insert / read / rollback", True)
    except Exception as exc:
        check("Insert / read / rollback", False, str(exc))

    # 6. DB file on disk
    print("\n[6] Database file on disk")
    sep()
    db_path = os.path.join(os.path.dirname(__file__), "credit_assistant.db")
    exists = os.path.isfile(db_path)
    size_kb = round(os.path.getsize(db_path) / 1024, 1) if exists else 0
    check(
        "credit_assistant.db exists",
        exists,
        f"size: {size_kb} KB" if exists else "file not found",
    )

    # Summary
    passed = sum(_results)
    total = len(_results)
    sep("=")
    if passed == total:
        print(f"  RESULT: ALL {total} CHECKS PASSED")
    else:
        print(f"  RESULT: {passed}/{total} PASSED -- review failures above")
    sep("=")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
