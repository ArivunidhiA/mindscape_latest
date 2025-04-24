from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

def generate_pdf_report(assessment, user):
    """
    Generate a PDF report for the assessment results.
    
    Args:
        assessment (Assessment): The assessment object containing scores
        user (User): The user who took the assessment
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create PDF directory if it doesn't exist
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'assessment_report_{user.id}_{timestamp}.pdf'
    filepath = os.path.join(pdf_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Assessment Report", title_style))
    
    # Add user information
    story.append(Paragraph(f"User: {user.username}", styles['Normal']))
    story.append(Paragraph(f"Date: {assessment.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Create scores table
    data = [['Dimension', 'Score']]
    for dimension, score in assessment.scores.items():
        data.append([dimension.replace('_', ' ').title(), f"{score:.2f}"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Add interpretation
    interpretation_style = ParagraphStyle(
        'CustomInterpretation',
        parent=styles['Normal'],
        fontSize=12,
        leading=16
    )
    story.append(Paragraph("Interpretation:", styles['Heading2']))
    story.append(Paragraph(
        "This assessment measures your competencies across five key dimensions. "
        "Scores range from 1 to 5, with higher scores indicating stronger competencies. "
        "Use these results to identify areas of strength and opportunities for development.",
        interpretation_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return f'/static/pdfs/{filename}' 