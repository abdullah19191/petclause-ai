# utils/pdf.py

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import uuid


def create_pdf(
    path,
    listing,
    fixed,
    risky,
    citations,
    city=None,
    version="1.0.0"
):
    """
    Generate a professional, legal-style PDF report.

    This version is formatted for attorneys, compliance teams,
    and regulatory filings. Court-readable and audit-friendly.
    """

    # ---------------------------
    # DOCUMENT TEMPLATE
    # ---------------------------
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        title="PetClause AI Compliance Report",
        author="PetClause AI",
        leftMargin=55,
        rightMargin=55,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom style overrides for legal format
    h1 = ParagraphStyle(
        "Heading1",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=10
    )
    h2 = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=8
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15
    )

    content = []

    # ---------------------------
    # TITLE PAGE
    # ---------------------------
    doc_id = uuid.uuid4().hex[:10].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    title_data = [
        ["📄 PetClause AI — Rental Compliance Report"],
        [f"Jurisdiction: {city if city else 'N/A'}"],
        [f"Document ID: {doc_id}"],
        [f"Version: {version}"],
        [f"Generated: {timestamp}"],
    ]

    table = Table(title_data, colWidths=[450])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 16),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (0, 0), 12),
        ("TOPPADDING", (0, 0), (0, 0), 12),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f3f4f6")),
        ("FONTSIZE", (0, 1), (0, -1), 10),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 1), (0, -1), colors.black),
    ]))
    content.append(table)
    content.append(Spacer(1, 20))

    # ---------------------------
    # RISKY CLAUSES
    # ---------------------------
    content.append(Paragraph("⚠️ Identified Risk Clauses", h2))

    if risky:
        for r in risky:
            content.append(Paragraph(f"• {r}", body))
    else:
        content.append(Paragraph("No illegal or non-compliant clauses detected.", body))

    content.append(Spacer(1, 20))

    # ---------------------------
    # FIXED LISTING
    # ---------------------------
    content.append(Paragraph("🛠️ Legally Corrected Listing", h2))
    content.append(Paragraph(fixed.replace("\n", "<br/>"), body))
    content.append(Spacer(1, 20))

    # ---------------------------
    # LEGAL CITATIONS
    # ---------------------------
    content.append(Paragraph("📚 Legal Citations Used", h2))

    if citations:
        for cite in citations:
            content.append(Paragraph(f"• {cite}", body))
    else:
        content.append(Paragraph("No formal citations returned from AI model.", body))

    content.append(Spacer(1, 20))

    # ---------------------------
    # FULL ORIGINAL TEXT
    # ---------------------------
    if len(listing.split()) > 120:   # ~120 words threshold
     content.append(PageBreak())
    else:
     content.append(Spacer(1, 30))

    content.append(Paragraph("📄 Original Listing Reviewed", h2))
    content.append(Paragraph(listing.replace("\n", "<br/>"), body))
    content.append(Spacer(1, 20))

    # ---------------------------
    # LEGAL DISCLAIMER
    # ---------------------------
    disclaimer = """
    <b>Disclaimer:</b><br/>
    This report is provided for informational purposes only and does not constitute legal advice.
    Laws vary by jurisdiction and may change without notice. Always consult a licensed attorney
    for legal matters or before signing any housing agreement. PetClause AI is not a law firm.
    """
    content.append(Paragraph(disclaimer, body))

    # ---------------------------
    # BUILD PDF
    # ---------------------------
    doc.build(content)
