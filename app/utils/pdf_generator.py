import os
from datetime import datetime
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import numpy as np

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.colors import HexColor

def create_radar_chart(categories, scores, max_score=5):
    """
    Create a radar chart for the assessment scores.
    
    Args:
        categories (list): List of category names
        scores (list): List of scores corresponding to categories
        max_score (int): Maximum possible score for any category
        
    Returns:
        BytesIO: PNG image data of the radar chart
    """
    try:
        # Input validation
        if not categories or not scores:
            print("Error: Empty categories or scores")
            return None
            
        if len(categories) != len(scores):
            print("Error: Categories and scores must have the same length")
            return None
            
        # Validate scores are numeric and within range
        try:
            scores = [float(score) for score in scores]
            if any(score < 0 or score > max_score for score in scores):
                print("Error: Scores must be between 0 and max_score")
                return None
        except (ValueError, TypeError):
            print("Error: Invalid score values")
            return None
            
        # Format category labels
        categories = [cat.replace('_', ' ').title() for cat in categories]
            
        # Set up the plot with a default style
        plt.style.use('default')  # Use default style instead of dark_background
        fig = plt.figure(figsize=(8, 8), facecolor='none')  # Transparent background
        ax = fig.add_subplot(111, projection='polar')
        
        # Calculate angles for the radar chart
        num_vars = len(categories)
        angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
        
        # Close the plot by appending first value
        scores = np.array(scores)
        scores = np.concatenate((scores, [scores[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        
        # Plot data with enhanced styling
        ax.plot(angles, scores, 'o-', linewidth=2.5, color='#9370DB', label='Scores')
        ax.fill(angles, scores, alpha=0.25, color='#9370DB')
        
        # Set chart properties
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color='black', size=10)  # Black text for better visibility
        ax.set_ylim(0, max_score)
        
        # Customize grid
        ax.grid(True, color='gray', alpha=0.3)
        ax.spines['polar'].set_color('gray')
        ax.tick_params(axis='y', colors='black')  # Black text for better visibility
        
        # Add title
        plt.title('Assessment Results', pad=20, color='black', size=14)  # Black text for better visibility
        
        # Save plot to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                   facecolor='none', edgecolor='none', transparent=True)  # Transparent background
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        print(f"Error creating radar chart: {str(e)}")
        return None

def create_bar_chart(categories, scores, max_score=5):
    """Create a bar chart for the assessment scores."""
    try:
        if not categories or not scores:
            return None
            
        categories = [cat.replace('_', ' ').title() for cat in categories]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1a1a1a')
        
        x = np.arange(len(categories))
        bars = ax.bar(x, scores, color='#9370DB', alpha=0.7)
        
        ax.set_ylim(0, max_score)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right', color='white')
        
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', color='white')
        
        plt.title('Assessment Results', pad=20, color='white', size=14)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                   facecolor='#1a1a1a', edgecolor='none')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        print(f"Error creating bar chart: {str(e)}")
        return None

def generate_pdf_report(assessment, user, assessment_info, category_scores):
    # Create directory if it doesn't exist
    output_dir = os.path.join('app', 'static', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{user.name}_{assessment['name']}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create the PDF document with custom margins
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=HexColor('#333333')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=6,
        spaceAfter=6,
        leading=16
    )
    
    # Title
    story.append(Paragraph(f"{assessment['name']} Assessment Results", title_style))
    
    # Basic Information
    story.append(Paragraph("Assessment Information", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {user.name}", normal_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph(f"<b>Email:</b> {user.email if hasattr(user, 'email') else 'N/A'}", normal_style))
    story.append(Spacer(1, 20))
    
    # Assessment Description
    story.append(Paragraph("Assessment Description", heading_style))
    story.append(Paragraph(assessment_info['description'], normal_style))
    story.append(Spacer(1, 20))
    
    # Category Scores
    story.append(Paragraph("Category Scores", heading_style))
    
    # Create table data
    table_data = [['Category', 'Score']]
    categories = []
    scores = []
    for category, score in category_scores.items():
        formatted_category = category.replace('_', ' ').title()
        table_data.append([formatted_category, f"{score:.2f}"])
        categories.append(formatted_category)
        scores.append(score)
    
    # Calculate overall average
    overall_score = sum(category_scores.values()) / len(category_scores)
    table_data.append(['Overall Average', f"{overall_score:.2f}"])
    
    # Create and style the table
    table = Table(table_data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4A4A4A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#E8E8E8')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [HexColor('#FFFFFF'), HexColor('#F5F5F5')]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Add visualizations
    story.append(Paragraph("Visual Representation", heading_style))
    
    # Create and add radar chart
    radar_buffer = create_radar_chart(categories, scores)
    if radar_buffer:
        radar_img = Image(radar_buffer, width=6*inch, height=6*inch)
        story.append(radar_img)
    
    story.append(PageBreak())
    
    # Create and add bar chart
    bar_buffer = create_bar_chart(categories, scores)
    if bar_buffer:
        bar_img = Image(bar_buffer, width=7*inch, height=4*inch)
        story.append(bar_img)
    
    story.append(Spacer(1, 30))
    
    # Interpretation
    story.append(Paragraph("Score Interpretation", heading_style))
    interpretation = get_score_interpretation(overall_score)
    story.append(Paragraph(interpretation, normal_style))
    
    # Recommendations section
    story.append(Paragraph("Recommendations", heading_style))
    recommendations = get_recommendations(category_scores)
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", normal_style))
    
    # Build the PDF
    doc.build(story)
    
    return f"/static/reports/{filename}"

def get_score_interpretation(score):
    if score >= 4.5:
        return "Excellent: You demonstrate exceptional understanding and capability in this area."
    elif score >= 3.5:
        return "Good: You show strong competency with room for some improvement."
    elif score >= 2.5:
        return "Average: You have a basic understanding but there's significant room for development."
    elif score >= 1.5:
        return "Below Average: You may benefit from focused attention and improvement in this area."
    else:
        return "Needs Improvement: Consider seeking additional support and resources in this area."

def get_recommendations(category_scores):
    """Generate specific recommendations based on category scores."""
    recommendations = []
    
    for category, score in category_scores.items():
        formatted_category = category.replace('_', ' ').title()
        if score < 2.5:
            recommendations.append(
                f"Focus on improving {formatted_category} through targeted practice and learning resources."
            )
        elif score < 3.5:
            recommendations.append(
                f"Consider additional training in {formatted_category} to enhance your capabilities."
            )
        elif score < 4.5:
            recommendations.append(
                f"While you show good competency in {formatted_category}, there's room for refinement."
            )
    
    if not recommendations:
        recommendations.append(
            "Maintain your excellent performance across all categories and consider mentoring others."
        )
    
    return recommendations 