# utils/pdf.py — PROFESSIONAL & GORGEOUS VERSION (2025)
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import textwrap
import os
from datetime import datetime

def create_pdf(path, listing, fixed, risky, citations, city=None, logo_path="assets/PetClause_AI_logo.jpg"):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER
    styles = getSampleStyleSheet()

    # ====================== CUSTOM PROFESSIONAL STYLES ======================
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=20,
        textColor=colors.HexColor("#1e40af"),
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor("#1e40af"),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor("#1e40af"),
        leftIndent=0
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=10,
        textColor=colors.HexColor("#1f2937")
    )
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=body_style,
        backColor=colors.HexColor("#fef3c7"),
        borderPadding=8,
        borderColor=colors.HexColor("#f59e0b"),
        borderWidth=1,
        borderRadius=6
    )

    # ====================== HEADER WITH LOGO ======================
    y = height - 80

    # Logo (top-left)
    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 50, height - 120, width=120, preserveAspectRatio=True, mask='auto')
        except:
            pass

    # Title (centered)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#1e40af"))
    c.drawCentredString(width / 2, height - 100, "PetClause AI")
    
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(width / 2, height - 130, "Pet Policy Compliance Report")

    if city:
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#1e40af"))
        c.drawCentredString(width / 2, height - 160, f"Jurisdiction: {city}, USA")

    # Top accent line
    c.setStrokeColor(colors.HexColor("#3b82f6"))
    c.setLineWidth(4)
    c.line(50, height - 180, width - 50, height - 180)

    y = height - 210

    # ====================== SECTION: Risky Clauses ======================
    def add_section(title, icon):
        nonlocal y
        c.setFillColor(colors.HexColor("#1e40af"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"{icon} {title}")
        y -= 30
        c.setStrokeColor(colors.HexColor("#e5e7eb"))
        c.setLineWidth(1)
        c.line(50, y + 5, width - 50, y + 5)
        y -= 15

    add_section("Risky or Illegal Clauses Detected", "Warning")

    if risky:
        for phrase in risky:
            para = Paragraph(f"• {phrase.strip()}", highlight_style)
            para.wrapOn(c, width - 100, 200)
            para.drawOn(c, 60, y - 20)
            y -= para.height + 15
            if y < 100:
                c.showPage()
                y = height - 80
    else:
        c.setFont("Helvetica-Oblique", 12)
        c.setFillColor(colors.HexColor("#16a34a"))
        c.drawString(60, y, "No risky or illegal pet clauses detected.")
        y -= 30

    # ====================== SECTION: Corrected Listing ======================
    add_section("Recommended Compliant Pet Policy", "Checkmark")

    # Boxed compliant text
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#3b82f6"))
    c.setLineWidth(2)
    c.roundRect(48, y - 40, width - 96, 180, 12, stroke=1, fill=1)

    c.setFillColor(colors.HexColor("#1e40af"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(65, y - 15, "Use this exact wording in your listing:")

    lines = fixed.strip().split("\n")
    line_y = y - 45
    for line in lines:
        if line.strip():
            c.setFont("Helvetica", 11.5)
            c.setFillColor(colors.HexColor("#1f2937"))
            wrapped = textwrap.wrap(line.strip(), 88)
            for wline in wrapped:
                c.drawString(65, line_y, wline)
                line_y -= 18
        else:
            line_y -= 10
    y = line_y - 30

    # ====================== SECTION: Legal Basis ======================
    add_section("Legal Citations & Authority", "Book")

    if citations:
        for cite in citations:
            para = Paragraph(f"• {cite}", body_style)
            para.wrapOn(c, width - 120, 200)
            para.drawOn(c, 60, y - 10)
            y -= para.height + 8
            if y < 120:
                c.showPage()
                y = height - 80
    else:
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(colors.grey)
        c.drawString(60, y, "Analysis based on current FHA, local ordinances, and case law.")
        y -= 30

    # ====================== FINAL FOOTER ======================
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica-Oblique", 9)
    footer = f"Generated by PetClause AI • {datetime.now().strftime('%B %d, %Y at %I:%M %p')} • Not legal advice • For compliance guidance only"
    c.drawCentredString(width / 2, 40, footer)

    # Blue bottom line
    c.setStrokeColor(colors.HexColor("#3b82f6"))
    c.setLineWidth(4)
    c.line(50, 55, width - 50, 55)

    c.save()