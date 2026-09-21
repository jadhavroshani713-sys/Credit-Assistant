"""
CREDIT ASSISTANT - Gemini AI Recommendations
Phase 5: AI Integration

Provides structured credit-health recommendations using the official Google GenAI SDK.
Includes full error handling and contextual fallback generation.
"""

import json
import logging
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fallback models in priority order
_GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def build_credit_prompt(profile: Any, user_name: str = "User") -> str:
    """
    Construct an educational prompt for Gemini based on the user's financial profile.
    Tailored to the Indian credit ecosystem (CIBIL/Experian, RBI guidelines).
    """
    score = profile.credit_score if profile.credit_score is not None else "Not provided"
    util = f"{profile.utilization:.1f}%" if profile.utilization is not None else "Not provided"
    missed = profile.missed_payments if profile.missed_payments is not None else 0
    loans = profile.active_loans if profile.active_loans is not None else 0
    salary = f"INR {profile.monthly_salary:,.2f}" if profile.monthly_salary is not None else "Not provided"
    expenses = f"INR {profile.monthly_expenses:,.2f}" if profile.monthly_expenses is not None else "Not provided"
    dti = f"{profile.debt_to_income:.1f}%" if profile.debt_to_income is not None else "Not provided"
    limit = f"INR {profile.credit_limit:,.2f}" if profile.credit_limit is not None else "Not provided"
    used = f"INR {profile.credit_used:,.2f}" if profile.credit_used is not None else "Not provided"

    prompt = f"""
You are an expert, empathetic financial and credit counselor specialized in the Indian banking and credit ecosystem (CIBIL, Experian, RBI credit guidelines).
Analyze the following financial profile for {user_name} and provide educational, actionable guidance on improving credit health.

Financial Profile:
- Credit Score: {score} (Range: 300 - 900)
- Total Credit Limit: {limit}
- Current Credit Used: {used}
- Credit Utilization Ratio: {util}
- Missed / Overdue Payments: {missed}
- Active Loan Accounts: {loans}
- Monthly Income / Salary: {salary}
- Monthly Necessary Expenses: {expenses}
- Debt-to-Income (DTI) Ratio: {dti}

Guidelines:
1. Act as an educational credit assistant explaining credit-health metrics.
2. Do NOT make guaranteed financial predictions or promise specific score numbers.
3. Keep advice realistic and specific to the Indian credit context (e.g., credit bureau reporting, full vs minimum payment, loan settlement vs closure with NOC).
4. Return ONLY a valid JSON object with EXACTLY these four keys:
   - "overall_assessment": A concise paragraph (3-4 sentences) assessing their overall credit health and standing.
   - "critical_issues": A list of exactly 3 prominent risks or bottlenecks observed in their metrics (or key focus areas if metrics are good).
   - "recommendations": A list of exactly 5 specific, high-impact, actionable steps to improve credit score and reduce debt.
   - "improvement_guidance": A concise summary (2-3 sentences) on the expected timeline and priority actions for sustainable score improvement.

Return ONLY raw JSON. Do not include markdown code block syntax like ```json or other text outside the JSON.
"""
    return prompt.strip()


def generate_fallback_recommendations(profile: Any, user_name: str = "User", reason: str = "") -> Dict[str, Any]:
    """
    Generate deterministic, rule-based credit guidance when Gemini is unavailable.
    Ensures the user always receives a professional, highly relevant response.
    """
    score = profile.credit_score or 650
    util = profile.utilization or 0.0
    missed = profile.missed_payments or 0
    dti = profile.debt_to_income or 0.0
    loans = profile.active_loans or 0

    # Assessment
    if score >= 750:
        assessment = (
            f"Your credit profile demonstrates strong financial discipline with a healthy score of {score}. "
            "You are in a prime position to qualify for the most competitive interest rates and premium credit products. "
            "Maintaining these responsible credit habits will safeguard your financial standing."
        )
    elif score >= 650:
        assessment = (
            f"Your credit profile is currently moderate with a score of {score}. "
            "While you may qualify for standard credit cards and loans, high utilization or past delays "
            "could be limiting your access to preferred interest rates. Targeted actions can elevate you into the 750+ tier."
        )
    else:
        assessment = (
            f"Your credit score is currently at {score}, indicating potential distress or high credit risk. "
            "Lenders may hesitate or charge elevated interest rates on new credit applications. "
            "With focused debt management and timely payments, credit rehabilitation is fully achievable over time."
        )

    # Critical issues
    issues = []
    if missed > 0:
        issues.append(f"Recorded {missed} missed/late payment(s), severely dampening your credit score in bureau records.")
    if util > 30.0:
        issues.append(f"High credit utilization at {util:.1f}%, exceeding the RBI-recommended benchmark of 30%.")
    if dti > 40.0:
        issues.append(f"Elevated Debt-to-Income (DTI) ratio at {dti:.1f}%, leaving constrained liquidity for emergency savings.")
    if loans >= 3:
        issues.append(f"Multiple ({loans}) active loan accounts creating continuous monthly liability and leverage strain.")

    default_issues = [
        "Credit utilization needs continuous vigilance to remain below the 30% safety threshold.",
        "A lack of diverse credit mix (unsecured vs secured loans) can constrain maximum score potential.",
        "Frequent hard credit inquiries by financial institutions can temporarily lower credit scores.",
    ]
    for di in default_issues:
        if len(issues) >= 3:
            break
        if di not in issues:
            issues.append(di)

    recs = [
        "Pay credit card statements in full prior to the due date rather than paying only the Minimum Amount Due.",
        "Aim to keep credit card utilization below 30% of your sanctioned limit on each card.",
        "Set up standing auto-debit instructions for all loan EMIs to avoid accidental 30+ DPD (Days Past Due) reporting.",
        "Prioritize repaying highest-interest revolving credit or personal loans to swiftly improve your Debt-to-Income ratio.",
        "Check your CIBIL/Experian credit reports periodically to identify and dispute any reporting errors or unauthorized accounts.",
    ]

    guidance = (
        "In the Indian banking framework, positive credit behaviors like punctual EMI repayments and low utilization "
        "typically reflect on bureau scores within 3 to 6 billing cycles. Prioritize clearing overdue amounts first."
    )

    if reason:
        logger.info("Using fallback credit recommendations (Reason: %s)", reason)

    return {
        "overall_assessment": assessment,
        "critical_issues": issues[:3],
        "recommendations": recs[:5],
        "improvement_guidance": guidance,
    }


def get_recommendations_from_gemini(profile: Any, user_name: str = "User") -> Dict[str, Any]:
    """
    Call Gemini API using google-genai SDK.
    Falls back gracefully if key is missing, invalid, or API fails.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        logger.warning("GEMINI_API_KEY is not configured. Serving intelligent fallback recommendations.")
        return generate_fallback_recommendations(profile, user_name, reason="API key not configured")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = build_credit_prompt(profile, user_name)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        )

        response = None
        last_err = None

        for model_name in _GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    break
            except Exception as e:
                last_err = e
                logger.warning("Model %s failed: %s. Trying next model...", model_name, e)

        if not response or not response.text:
            logger.error("All Gemini models failed or returned empty response. Last error: %s", last_err)
            return generate_fallback_recommendations(profile, user_name, reason="Gemini response empty/failed")

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)

        parsed = json.loads(raw_text)

        required_keys = ["overall_assessment", "critical_issues", "recommendations", "improvement_guidance"]
        if not all(k in parsed for k in required_keys):
            logger.warning("Gemini returned JSON with missing keys: %s", parsed.keys())
            return generate_fallback_recommendations(profile, user_name, reason="Missing schema keys in AI response")

        if not isinstance(parsed["critical_issues"], list):
            parsed["critical_issues"] = [str(parsed["critical_issues"])]
        if not isinstance(parsed["recommendations"], list):
            parsed["recommendations"] = [str(parsed["recommendations"])]

        return {
            "overall_assessment": str(parsed["overall_assessment"]),
            "critical_issues": [str(x) for x in parsed["critical_issues"]][:3],
            "recommendations": [str(x) for x in parsed["recommendations"]][:5],
            "improvement_guidance": str(parsed["improvement_guidance"]),
        }

    except Exception as exc:
        logger.error("Gemini API invocation error: %s", exc, exc_info=True)
        return generate_fallback_recommendations(profile, user_name, reason=f"Gemini API exception: {str(exc)}")
