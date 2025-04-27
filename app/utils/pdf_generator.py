import os
from datetime import datetime
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import numpy as np

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
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
    """Generate a one-page A4 PDF report for assessment results."""
    try:
        print("\n=== Starting PDF Generation ===")
        
        pdf_dir = os.path.join(current_app.root_path, 'static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        os.chmod(pdf_dir, 0o755)
        
        # Use assessment name for the filename
        safe_name = assessment_info['name'].replace(' ', '_')
        filename = f"{safe_name}_Results.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        # If file exists, add a timestamp to make it unique
        if os.path.exists(filepath):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_name}_Results_{timestamp}.pdf"
            filepath = os.path.join(pdf_dir, filename)
        
        # Create PDF document with A4 size
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            spaceAfter=20,
            textColor=HexColor('#6B46C1')
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading1'],
            fontSize=12,
            textColor=HexColor('#9370DB')
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#4A5568')
        )
        
        story = []
        
        # Title
        title = f"{assessment_info['name']} Results"
        story.append(Paragraph(title, title_style))
        
        # User info in a table
        user_data = [
            ['User:', user.username],
            ['Date:', assessment.completed_at.strftime('%B %d, %Y at %I:%M %p')]
        ]
        user_table = Table(user_data, colWidths=[30*mm, 100*mm])
        user_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#4A5568')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 10*mm))
        
        # Create visualization based on assessment type
        visualization_type = assessment_info.get('visualization', 'radar')
        if visualization_type == 'bar':
            chart_data = create_bar_chart(
                categories=list(category_scores.keys()),
                scores=list(category_scores.values()),
                max_score=assessment_info['max_score']
            )
        else:  # default to radar
            chart_data = create_radar_chart(
                categories=list(category_scores.keys()),
                scores=list(category_scores.values()),
                max_score=assessment_info['max_score']
            )
        
        if chart_data:
            img = Image(chart_data)
            # Adjust image size to fit A4
            img.drawHeight = 120*mm
            img.drawWidth = 160*mm
            story.append(img)
        
        story.append(Spacer(1, 10*mm))
        
        # Category scores in a table
        story.append(Paragraph('Detailed Scores', heading_style))
        story.append(Spacer(1, 5*mm))
        
        score_data = [[Paragraph('Category', heading_style), Paragraph('Score', heading_style)]]
        for category, score in category_scores.items():
            category_name = category.replace('_', ' ').title()
            score_data.append([
                Paragraph(category_name, normal_style),
                Paragraph(f"{score:.1f} / {assessment_info['max_score']}", normal_style)
            ])
        
        score_table = Table(score_data, colWidths=[120*mm, 40*mm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#4A5568')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0'))
        ]))
        story.append(score_table)
        
        # Build the PDF
        doc.build(story)
        os.chmod(filepath, 0o644)
        
        if os.path.exists(filepath):
            return f'/static/pdfs/{filename}'
        return None
            
    except Exception as e:
        print(f"Error in PDF Generation: {str(e)}")
        return None 