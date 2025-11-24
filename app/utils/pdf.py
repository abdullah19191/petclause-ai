# utils/pdf.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

def create_pdf(path, listing, fixed, risky, citations):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PetClause AI – Compliance Report")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Risky Clauses Found:")
    y -= 20

    for r in risky:
        for line in textwrap.wrap(r, 90):
            c.drawString(60, y, f"- {line}")
            y -= 15

    y -= 20
    c.drawString(50, y, "Fixed Listing:")
    y -= 20

    for line in textwrap.wrap(fixed, 95):
        c.drawString(60, y, line)
        y -= 15

    y -= 20
    c.drawString(50, y, "Citations:")
    y -= 20

    for cite in citations:
        for line in textwrap.wrap(cite, 95):
            c.drawString(60, y, line)
            y -= 15

    c.save()
