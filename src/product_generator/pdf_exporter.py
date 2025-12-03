"""
PDF Exporter

Converts markdown content to PDF using reportlab.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

def markdown_to_pdf(markdown_content: str, output_path: str, title: str = "Digital Product"):
    """
    Convert markdown to PDF.
    
    Note: This is a simplified converter. For full markdown support,
    consider using markdown2 + weasyprint or similar.
    """
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for PDF elements
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#34495E',
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = styles['BodyText']
    body_style.fontSize = 11
    body_style.leading = 14
    
    # Parse markdown (simplified)
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 0.2*inch))
            continue
        
        # Title (# )
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 0.3*inch))
        
        # Heading (## )
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))
        
        # Bullet point
        elif line.startswith('- '):
            text = "• " + line[2:].strip()
            story.append(Paragraph(text, body_style))
        
        # Horizontal rule
        elif line.startswith('---'):
            story.append(Spacer(1, 0.3*inch))
        
        # Regular paragraph
        elif line.startswith('*') and line.endswith('*'):
            # Italic text
            text = "<i>" + line[1:-1] + "</i>"
            story.append(Paragraph(text, body_style))
        else:
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF created: {output_path}")
