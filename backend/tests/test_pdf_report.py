"""
CREDIT ASSISTANT - Technical Architecture Tests
Tests for:
  - PDF Generation Service (ReportLab)
  - GET /report/{user_id} (Financial Health Report JSON)
  - GET /report/pdf/{user_id} (Download Generated PDF)
  - Multi-Provider AI Fallback
"""

import io
from pdf_service import generate_credit_report_pdf

REG_PAYLOAD = {
    "name": "Dev Sharma",
    "email": "dev.sharma@testmail.com",
    "mobile": "9876543210",
    "password": "Password123!",
}

FIN_PAYLOAD = {
    "credit_score": 740,
    "credit_limit": 200000.0,
    "credit_used": 45000.0,
    "missed_payments": 0,
    "active_loans": 1,
    "monthly_salary": 90000.0,
    "monthly_expenses": 30000.0,
}


def setup_user(client, submit_fin=True):
    reg = client.post("/register", json=REG_PAYLOAD)
    assert reg.status_code == 201
    uid = reg.json()["id"]

    if submit_fin:
        fin = client.post("/financial-data", json={"user_id": uid, **FIN_PAYLOAD})
        assert fin.status_code == 201

    return uid


# ===========================================================================
# 1. Financial Health Report JSON Tests
# ===========================================================================

def test_financial_report_json_success(client):
    """GET /report/{user_id} returns structured JSON report."""
    uid = setup_user(client, submit_fin=True)

    r = client.get(f"/report/{uid}")
    assert r.status_code == 200
    data = r.json()

    assert data["user"]["id"] == uid
    assert data["profile"]["credit_score"] == 740
    assert data["profile"]["utilization"] == 22.5  # 45k / 200k * 100
    assert data["profile"]["debt_to_income"] == 33.33  # 30k / 90k * 100
    assert "pdf_download_url" in data
    assert data["pdf_download_url"] == f"/report/pdf/{uid}"
    assert data["status"] == "generated"
    assert "ai_recommendations" in data
    assert len(data["ai_recommendations"]["recommendations"]) == 5


def test_financial_report_json_no_profile(client):
    """GET /report/{user_id} for user without financial data returns pending_data."""
    uid = setup_user(client, submit_fin=False)

    r = client.get(f"/report/{uid}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_data"
    assert data["profile"] is None


def test_financial_report_json_nonexistent_user(client):
    """GET /report/999999 returns 404."""
    r = client.get("/report/999999")
    assert r.status_code == 404


# ===========================================================================
# 2. PDF Report Generation & Download Tests
# ===========================================================================

def test_download_pdf_report_success(client):
    """GET /report/pdf/{user_id} streams a valid binary PDF document."""
    uid = setup_user(client, submit_fin=True)

    r = client.get(f"/report/pdf/{uid}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers.get("content-disposition", "")
    assert r.content.startswith(b"%PDF")  # Standard PDF magic header
    assert len(r.content) > 1000  # Non-empty complete PDF


def test_download_pdf_report_no_profile(client):
    """GET /report/pdf/{user_id} returns 404 if user has no profile data."""
    uid = setup_user(client, submit_fin=False)

    r = client.get(f"/report/pdf/{uid}")
    assert r.status_code == 404
    assert "without financial profile" in r.json()["detail"].lower()


def test_download_pdf_report_nonexistent_user(client):
    """GET /report/pdf/999999 returns 404."""
    r = client.get("/report/pdf/999999")
    assert r.status_code == 404


# ===========================================================================
# 3. Direct PDF Service Unit Test
# ===========================================================================

def test_pdf_service_direct_generation():
    """Verify generate_credit_report_pdf builds a valid PDF buffer."""
    from datetime import datetime, timezone

    class MockUser:
        id = 42
        name = "Aarav Patel"
        email = "aarav@example.com"
        mobile = "9876543210"
        created_at = datetime.now(timezone.utc)

    class MockProfile:
        credit_score = 780
        credit_limit = 500000.0
        credit_used = 60000.0
        utilization = 12.0
        monthly_salary = 150000.0
        monthly_expenses = 40000.0
        debt_to_income = 26.67
        missed_payments = 0
        active_loans = 1

    ai_dict = {
        "overall_assessment": "Excellent financial standing with prime credit score.",
        "critical_issues": ["Maintain current low utilization under 15%."],
        "recommendations": [
            "Continue paying bills before due date.",
            "Maintain current debt-to-income balance.",
            "Consider long-term wealth investments.",
            "Audit bureau records annually.",
            "Keep credit accounts active.",
        ],
        "improvement_guidance": "Consistent practices will maintain score in top percentile.",
    }

    buf = generate_credit_report_pdf(MockUser(), MockProfile(), [], ai_dict)
    assert isinstance(buf, io.BytesIO)
    content = buf.getvalue()
    assert content.startswith(b"%PDF")
    assert len(content) > 2000
