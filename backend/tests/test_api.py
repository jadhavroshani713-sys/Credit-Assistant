"""
CREDIT ASSISTANT - Phase 4 Automated Tests
==========================================

14 required test scenarios:

 1.  Health endpoint
 2.  Successful registration
 3.  Duplicate registration
 4.  Successful login
 5.  Invalid login
 6.  Financial data submission
 7.  DTI calculation
 8.  Credit utilisation calculation
 9.  First score history entry (old_score = None)
10.  Subsequent score history entry (improvement tracked)
11.  Dashboard retrieval
12.  Non-existent user (404)
13.  Zero salary (no crash)
14.  Zero credit limit (no crash)

NOTE: email-validator rejects reserved TLDs (.test, .local, .example).
      We use real-format domains (.com) in test payloads.
"""

# ---------------------------------------------------------------------------
# Shared test payloads
# ---------------------------------------------------------------------------

REG_PAYLOAD = {
    "name": "Alice Tester",
    "email": "alice.tester@testmail.com",
    "mobile": "9000000001",
    "password": "AlicePass123",
}

FIN_PAYLOAD_BASE = {
    "credit_score": 720,
    "credit_limit": 100000.0,
    "credit_used": 35000.0,
    "missed_payments": 0,
    "active_loans": 2,
    "monthly_salary": 60000.0,
    "monthly_expenses": 25000.0,
}

# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------

def register_user(client, payload=None):
    """Register a user and return the response JSON. Asserts 201."""
    payload = payload or REG_PAYLOAD
    r = client.post("/register", json=payload)
    assert r.status_code == 201, f"Register failed ({r.status_code}): {r.text}"
    return r.json()


def submit_finance(client, user_id, extra=None):
    """Submit financial data for user_id and return the response JSON."""
    payload = {"user_id": user_id, **FIN_PAYLOAD_BASE, **(extra or {})}
    r = client.post("/financial-data", json=payload)
    assert r.status_code == 201, f"Finance submit failed ({r.status_code}): {r.text}"
    return r.json()


def register_and_finance(client, credit_score=720, extra_fin=None):
    """Register Alice, submit one financial record, return (user_id, fin_resp)."""
    user = register_user(client)
    uid = user["id"]
    fin = submit_finance(client, uid, {"credit_score": credit_score, **(extra_fin or {})})
    return uid, fin


# ===========================================================================
# TEST 1 — Health endpoint
# ===========================================================================

def test_01_health(client):
    """GET /health returns 200 and status=ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ===========================================================================
# TEST 2 — Successful registration
# ===========================================================================

def test_02_register_success(client):
    """POST /register with valid payload returns 201, safe user info, no password."""
    r = client.post("/register", json=REG_PAYLOAD)
    assert r.status_code == 201
    body = r.json()

    assert body["name"] == REG_PAYLOAD["name"]
    assert body["email"] == REG_PAYLOAD["email"]
    assert isinstance(body["id"], int)
    assert body["id"] >= 1

    # Password must NEVER be returned
    assert "password" not in body
    assert "password_hash" not in body


# ===========================================================================
# TEST 3 — Duplicate registration
# ===========================================================================

def test_03_duplicate_email(client):
    """Registering the same email twice returns 409 Conflict."""
    client.post("/register", json=REG_PAYLOAD)
    r = client.post("/register", json=REG_PAYLOAD)
    assert r.status_code == 409
    assert "already exists" in r.json()["detail"].lower()


# ===========================================================================
# TEST 4 — Successful login
# ===========================================================================

def test_04_login_success(client):
    """POST /login with correct credentials returns 200 and user info."""
    register_user(client)
    r = client.post("/login", json={
        "email": REG_PAYLOAD["email"],
        "password": REG_PAYLOAD["password"],
    })
    assert r.status_code == 200
    body = r.json()

    assert body["email"] == REG_PAYLOAD["email"]
    assert "user_id" in body
    assert isinstance(body["user_id"], int)

    # No password leak
    assert "password" not in body
    assert "password_hash" not in body


# ===========================================================================
# TEST 5 — Invalid login
# ===========================================================================

def test_05a_wrong_password(client):
    """Correct email but wrong password returns 401."""
    register_user(client)
    r = client.post("/login", json={
        "email": REG_PAYLOAD["email"],
        "password": "WrongPassword999",
    })
    assert r.status_code == 401


def test_05b_unknown_email(client):
    """Unknown email returns 401 (not 404) to prevent user enumeration."""
    r = client.post("/login", json={
        "email": "nobody@nowhere.com",
        "password": "AnyPassword1",
    })
    assert r.status_code == 401


# ===========================================================================
# TEST 6 — Financial data submission
# ===========================================================================

def test_06_financial_data_submission(client):
    """POST /financial-data stores the profile and returns a profile_id."""
    uid, fin = register_and_finance(client)

    assert fin["profile_id"] >= 1
    assert fin["user_id"] == uid
    assert fin["credit_score"] == 720
    assert "message" in fin
    # server-computed fields exist
    assert "utilization_pct" in fin
    assert "debt_to_income_pct" in fin


# ===========================================================================
# TEST 7 — DTI calculation
# ===========================================================================

def test_07_dti_calculation(client):
    """
    DTI = (monthly_expenses / monthly_salary) * 100, rounded to 2 dp.
    25000 / 60000 * 100 = 41.67
    """
    _, fin = register_and_finance(client)
    expected = round((25000 / 60000) * 100, 2)   # 41.67
    assert fin["debt_to_income_pct"] == expected


# ===========================================================================
# TEST 8 — Credit utilisation calculation
# ===========================================================================

def test_08_utilisation_calculation(client):
    """
    utilization = (credit_used / credit_limit) * 100, rounded to 2 dp.
    35000 / 100000 * 100 = 35.0
    """
    _, fin = register_and_finance(client)
    expected = round((35000 / 100000) * 100, 2)   # 35.0
    assert fin["utilization_pct"] == expected


# ===========================================================================
# TEST 9 — First score history entry
# ===========================================================================

def test_09_first_score_history(client):
    """
    First financial submission: old_score=None, improvement=None.
    No previous score to compare against.
    """
    uid, fin = register_and_finance(client, credit_score=700)

    # API response
    assert fin["score_improvement"] is None

    # Dashboard history
    r = client.get(f"/dashboard/{uid}")
    assert r.status_code == 200
    history = r.json()["score_history"]
    assert len(history) == 1
    assert history[0]["old_score"] is None
    assert history[0]["new_score"] == 700
    assert history[0]["improvement"] is None


# ===========================================================================
# TEST 10 — Subsequent score history entry
# ===========================================================================

def test_10_subsequent_score_history(client):
    """
    Second submission records old_score → new_score and correct improvement.
    700 → 740 = +40 improvement.
    """
    uid, _ = register_and_finance(client, credit_score=700)

    fin2 = submit_finance(client, uid, {"credit_score": 740})
    assert fin2["score_improvement"] == 40

    r = client.get(f"/dashboard/{uid}")
    history = r.json()["score_history"]
    assert len(history) == 2
    assert history[1]["old_score"] == 700
    assert history[1]["new_score"] == 740
    assert history[1]["improvement"] == 40


# ===========================================================================
# TEST 11 — Dashboard retrieval
# ===========================================================================

def test_11_dashboard(client):
    """GET /dashboard/{user_id} returns full structured data."""
    uid, _ = register_and_finance(client)
    r = client.get(f"/dashboard/{uid}")
    assert r.status_code == 200

    body = r.json()
    # Top-level keys
    assert "user" in body
    assert "profile" in body
    assert "score_history" in body
    assert body["has_financial_data"] is True

    # User section
    assert body["user"]["id"] == uid
    assert body["user"]["name"] == REG_PAYLOAD["name"]

    # Profile section
    assert body["profile"] is not None
    assert body["profile"]["credit_score"] == 720

    # No password leak anywhere in the response
    body_str = str(body)
    assert "password_hash" not in body_str
    assert "password" not in body_str


# ===========================================================================
# TEST 12 — Non-existent user
# ===========================================================================

def test_12a_dashboard_nonexistent_user(client):
    """GET /dashboard/999999 returns 404 when user does not exist."""
    r = client.get("/dashboard/999999")
    assert r.status_code == 404


def test_12b_financial_data_nonexistent_user(client):
    """POST /financial-data with unknown user_id returns 404."""
    r = client.post("/financial-data", json={"user_id": 999999, **FIN_PAYLOAD_BASE})
    assert r.status_code == 404


# ===========================================================================
# TEST 13 — Zero salary (no crash)
# ===========================================================================

def test_13_zero_salary(client):
    """monthly_salary=0 must not raise a division-by-zero error; DTI = 0.0."""
    user = register_user(client)
    r = client.post("/financial-data", json={
        "user_id": user["id"],
        **FIN_PAYLOAD_BASE,
        "monthly_salary": 0.0,
        "monthly_expenses": 0.0,
    })
    assert r.status_code == 201
    assert r.json()["debt_to_income_pct"] == 0.0


# ===========================================================================
# TEST 14 — Zero credit limit (no crash)
# ===========================================================================

def test_14_zero_credit_limit(client):
    """credit_limit=0 must not raise a division-by-zero error; utilization = 0.0."""
    user = register_user(client)
    r = client.post("/financial-data", json={
        "user_id": user["id"],
        **FIN_PAYLOAD_BASE,
        "credit_limit": 0.0,
        "credit_used": 0.0,
    })
    assert r.status_code == 201
    assert r.json()["utilization_pct"] == 0.0
