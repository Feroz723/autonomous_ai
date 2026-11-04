"""
PDF Exporter

Converts markdown content to PDF using reportlab.
"""

import html
import os

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def markdown_to_pdf(markdown_content: str, output_path: str, title: str = "Digital Product"):
    """Convert simple Markdown content to a PDF file."""
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor="#2C3E50",
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor="#34495E",
        spaceAfter=12,
        spaceBefore=12,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
    )

    for line in (markdown_content or "").splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2 * inch))
        elif line.startswith("# "):
            text = html.escape(line[2:].strip(), quote=False)
            story.append(Paragraph(text or html.escape(title), title_style))
            story.append(Spacer(1, 0.3 * inch))
        elif line.startswith("## "):
            story.append(Paragraph(html.escape(line[3:].strip(), quote=False), heading_style))
        elif line.startswith("- "):
            text = "&#8226; " + html.escape(line[2:].strip(), quote=False)
            story.append(Paragraph(text, body_style))
        elif line.startswith("---"):
            story.append(Spacer(1, 0.3 * inch))
        elif line.startswith("*") and line.endswith("*") and len(line) > 1:
            text = html.escape(line[1:-1], quote=False)
            story.append(Paragraph(f"<i>{text}</i>", body_style))
        else:
            story.append(Paragraph(html.escape(line, quote=False), body_style))

    doc.build(story)
    print(f"✅ PDF created: {output_path}")
