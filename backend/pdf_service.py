"""
CREDIT ASSISTANT - PDF Generation Service
Uses ReportLab to generate an official, branded Credit Health & Financial Advisory Report.
"""

import io
from datetime import datetime, timezone
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _get_rating_badge(score: int) -> tuple[str, colors.HexColor]:
    if score >= 750:
        return "EXCELLENT (Low Risk)", colors.HexColor("#16a34a")
    if score >= 680:
        return "GOOD (Prime Tier)", colors.HexColor("#0284c7")
    if score >= 600:
        return "FAIR (Moderate Risk)", colors.HexColor("#d97706")
    return "POOR (High Risk)", colors.HexColor("#dc2626")


def generate_credit_report_pdf(
    user: Any,
    profile: Any,
    history: List[Any],
    ai_recommendations: Dict[str, Any],
) -> io.BytesIO:
    """
    Generate a complete, professional Credit Health & Advisory PDF Report.
    Returns an in-memory BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_title = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    header_sub = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    sec_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=6,
    )
    body_text = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )
    list_item_style = ParagraphStyle(
        "ListItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )
    bold_label = ParagraphStyle(
        "BoldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # 1. Header Banner
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    header_table = Table(
        [
            [
                Paragraph("CREDIT ASSISTANT", header_title),
                Paragraph(f"<b>Report ID:</b> CA-REP-{user.id}-{int(datetime.now().timestamp())}<br/><b>Generated:</b> {generated_at}", header_sub),
            ]
        ],
        colWidths=[320, 220],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=14))

    # 2. User Information Card
    user_info = [
        [
            Paragraph("<b>Client Name:</b>", bold_label),
            Paragraph(user.name, body_text),
            Paragraph("<b>Mobile:</b>", bold_label),
            Paragraph(user.mobile or "Not provided", body_text),
        ],
        [
            Paragraph("<b>Email:</b>", bold_label),
            Paragraph(user.email, body_text),
            Paragraph("<b>Account Active Since:</b>", bold_label),
            Paragraph(user.created_at.strftime("%d %b %Y") if getattr(user, "created_at", None) else "N/A", body_text),
        ],
    ]
    u_table = Table(user_info, colWidths=[80, 190, 120, 150])
    u_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(u_table)
    story.append(Spacer(1, 14))

    # 3. Credit Score Highlight Block
    score = profile.credit_score or 0
    rating_text, rating_color = _get_rating_badge(score)
    score_data = [
        [
            Paragraph(f"<b>CIBIL / Experian Credit Score</b><br/><font size='26'><b>{score}</b></font><font size='10' color='#64748b'> / 900</font>", body_text),
            Paragraph(f"<b>Risk Assessment Tier</b><br/><font size='13' color='{rating_color.hexval()}'><b>{rating_text}</b></font><br/><font size='8' color='#64748b'>Benchmark: RBI Preferred ≥ 750</font>", body_text),
        ]
    ]
    score_table = Table(score_data, colWidths=[270, 270])
    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4") if score >= 680 else colors.HexColor("#fffbeb")),
            ("BOX", (0, 0), (-1, -1), 1.5, rating_color),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 4. Financial Health Metrics Table
    story.append(Paragraph("FINANCIAL HEALTH INDICATORS", sec_heading))
    limit = profile.credit_limit or 0.0
    used = profile.credit_used or 0.0
    util = profile.utilization or 0.0
    salary = profile.monthly_salary or 0.0
    expenses = profile.monthly_expenses or 0.0
    dti = profile.debt_to_income or 0.0
    missed = profile.missed_payments or 0
    loans = profile.active_loans or 0

    metrics_data = [
        [Paragraph("<b>Metric</b>", bold_label), Paragraph("<b>Value</b>", bold_label), Paragraph("<b>Recommended Benchmark</b>", bold_label), Paragraph("<b>Status</b>", bold_label)],
        [
            Paragraph("Credit Card Limit", body_text),
            Paragraph(f"INR {limit:,.2f}", body_text),
            Paragraph("Adequate liquidity buffer", body_text),
            Paragraph("Sanctioned", body_text),
        ],
        [
            Paragraph("Credit Used", body_text),
            Paragraph(f"INR {used:,.2f}", body_text),
            Paragraph("Pay in full monthly", body_text),
            Paragraph(f"Available: INR {max(0, limit - used):,.2f}", body_text),
        ],
        [
            Paragraph("Credit Utilization", bold_label),
            Paragraph(f"<b>{util:.1f}%</b>", body_text),
            Paragraph("≤ 30.0% of limit", body_text),
            Paragraph("<font color='#16a34a'>Optimal</font>" if util <= 30 else "<font color='#dc2626'>High Utilization</font>", body_text),
        ],
        [
            Paragraph("Monthly Net Income", body_text),
            Paragraph(f"INR {salary:,.2f}", body_text),
            Paragraph("Consistent cash flow", body_text),
            Paragraph("Verified", body_text),
        ],
        [
            Paragraph("Monthly Expenses", body_text),
            Paragraph(f"INR {expenses:,.2f}", body_text),
            Paragraph("Controlled discretionary spend", body_text),
            Paragraph(f"Savings: INR {max(0, salary - expenses):,.2f}", body_text),
        ],
        [
            Paragraph("Debt-to-Income (DTI)", bold_label),
            Paragraph(f"<b>{dti:.1f}%</b>", body_text),
            Paragraph("≤ 40.0% of income", body_text),
            Paragraph("<font color='#16a34a'>Healthy</font>" if dti <= 40 else "<font color='#dc2626'>Liquidity Strain</font>", body_text),
        ],
        [
            Paragraph("Overdue / Missed Payments", bold_label),
            Paragraph(str(missed), body_text),
            Paragraph("0 (Zero tolerance)", body_text),
            Paragraph("<font color='#16a34a'>Clean Record</font>" if missed == 0 else f"<font color='#dc2626'>{missed} DPD Event(s)</font>", body_text),
        ],
        [
            Paragraph("Active Loan Accounts", body_text),
            Paragraph(str(loans), body_text),
            Paragraph("Balanced credit mix", body_text),
            Paragraph(f"{loans} Open Accounts", body_text),
        ],
    ]
    m_table = Table(metrics_data, colWidths=[150, 120, 160, 110])
    m_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ])
    )
    story.append(m_table)
    story.append(Spacer(1, 14))

    # 5. Score Progression History (if available)
    if history and len(history) > 1:
        story.append(Paragraph("SCORE TRAJECTORY & AUDIT LOG", sec_heading))
        h_data = [[Paragraph("<b>Entry</b>", bold_label), Paragraph("<b>Old Score</b>", bold_label), Paragraph("<b>New Score</b>", bold_label), Paragraph("<b>Improvement</b>", bold_label), Paragraph("<b>Recorded Date</b>", bold_label)]]
        for i, h in enumerate(history[-5:], start=1):
            imp_text = f"+{h.improvement}" if (h.improvement and h.improvement > 0) else str(h.improvement or "—")
            imp_color = "#16a34a" if (h.improvement and h.improvement > 0) else "#334155"
            h_data.append([
                Paragraph(f"#{i}", body_text),
                Paragraph(str(h.old_score or "Initial"), body_text),
                Paragraph(str(h.new_score), body_text),
                Paragraph(f"<font color='{imp_color}'><b>{imp_text}</b></font>", body_text),
                Paragraph(h.recorded_at.strftime("%d %b %Y, %H:%M") if getattr(h, "recorded_at", None) else "—", body_text),
            ])
        h_table = Table(h_data, colWidths=[50, 110, 110, 120, 150])
        h_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(h_table)
        story.append(Spacer(1, 14))

    # 6. AI Credit Counseling & Action Plan
    story.append(KeepTogether([
        Paragraph("AI-POWERED FINANCIAL COUNSELING (Groq / OpenAI / Gemini)", sec_heading),
        Paragraph(ai_recommendations.get("overall_assessment", "Overall credit health assessed."), body_text),
        Spacer(1, 8),
    ]))

    # Critical issues
    crit_issues = ai_recommendations.get("critical_issues", [])
    if crit_issues:
        story.append(Paragraph("<b>Key Risk Bottlenecks:</b>", bold_label))
        for iss in crit_issues:
            story.append(Paragraph(f"• {iss}", list_item_style))
        story.append(Spacer(1, 8))

    # Actionable steps
    recs = ai_recommendations.get("recommendations", [])
    if recs:
        story.append(Paragraph("<b>Actionable Steps to Improve:</b>", bold_label))
        for idx, r in enumerate(recs, 1):
            story.append(Paragraph(f"{idx}. {r}", list_item_style))
        story.append(Spacer(1, 8))

    # Improvement guidance
    guidance = ai_recommendations.get("improvement_guidance")
    if guidance:
        story.append(Paragraph("<b>Expected Improvement Timeline:</b>", bold_label))
        story.append(Paragraph(guidance, body_text))
        story.append(Spacer(1, 14))

    # Disclaimer Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph(
        "<i>Disclaimer: This document is an educational financial assessment generated by Credit Assistant. "
        "It does not constitute a formal loan sanction or legal guarantee of credit score changes. "
        "Credit ratings are subject to official bureau verification (CIBIL / Experian / Equifax / CRIF High Mark).</i>",
        header_sub,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
