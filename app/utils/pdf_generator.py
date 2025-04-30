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

def generate_pdf_report(assessment, user, assessment_info, category_scores, interpretation):
    """Generate a PDF report for the assessment results."""
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.join(current_app.root_path, 'static', 'pdfs')
        os.makedirs(output_dir, exist_ok=True)
        print(f"PDF output directory: {output_dir}")
        
        # Use predefined abbreviations for assessment types
        assessment_abbreviations = {
            'lsi': 'LSI',
            'oci': 'OCI',
            'lpi': 'LPI',
            'influence': 'ISP'
        }
        
        # Get the correct abbreviation or fallback to cleaned name if not found
        assessment_abbr = assessment_abbreviations.get(assessment.assessment_type)
        if not assessment_abbr:
            # Fallback to previous logic if type not found
            clean_name = (assessment_info['name']
                         .replace('(', '')
                         .replace(')', '')
                         .replace('Leadership', '')
                         .strip())
            assessment_abbr = ''.join(word[0].upper() for word in clean_name.split())
            
        timestamp = datetime.now().strftime('%d%b%y')  # Format: 30Apr25
        filename = f"{assessment_abbr}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        print(f"Generating PDF at: {filepath}")
        
        # Create the PDF document with A4 size and custom margins
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=30*mm,
            leftMargin=30*mm,
            topMargin=30*mm,
            bottomMargin=30*mm
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=10*mm,
            alignment=1,  # Center alignment
            textColor=HexColor('#333333')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=8*mm,
            spaceAfter=4*mm,
            textColor=HexColor('#444444')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=2*mm,
            spaceAfter=2*mm,
            leading=14,
            textColor=HexColor('#333333')
        )
        
        # Title with assessment name
        story.append(Paragraph(assessment_info['name'], title_style))
        
        # User Information Table
        user_data = [
            ["Name:", user.name],
            ["Date:", assessment.completed_at.strftime('%B %d, %Y')],
            ["Email:", user.email if hasattr(user, 'email') else 'N/A']
        ]
        
        user_table = Table(user_data, colWidths=[80, 300])
        user_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 10*mm))
        
        # Results visualization - always use the same type as specified in assessment_info
        visualization_type = assessment_info.get('visualization', 'radar')  # Default to radar if not specified
        print(f"Using visualization type: {visualization_type}")
        
        if visualization_type == 'radar':
            chart_buffer = create_radar_chart(
                list(category_scores.keys()),
                list(category_scores.values()),
                assessment_info['max_score']
            )
        else:  # bar chart
            chart_buffer = create_bar_chart(
                list(category_scores.keys()),
                list(category_scores.values()),
                assessment_info['max_score']
            )
            
        if chart_buffer:
            img = Image(chart_buffer)
            # Adjust size based on chart type
            if visualization_type == 'radar':
                img.drawHeight = 140*mm  # Make radar chart slightly larger
                img.drawWidth = 140*mm
            else:
                img.drawHeight = 120*mm
                img.drawWidth = 160*mm
            story.append(img)
        
        story.append(Spacer(1, 5*mm))
        
        # Category Scores Table
        story.append(Paragraph("Detailed Scores", heading_style))
        data = [["Category", "Score"]]
        for category, score in category_scores.items():
            category_name = category.replace('_', ' ').title()
            data.append([
                category_name,
                f"{score:.1f}"
            ])
        
        table = Table(data, colWidths=[300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#444444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#333333')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        story.append(table)
        
        # Assessment Interpretation
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph("Your Assessment Insight", heading_style))
        story.append(Paragraph(interpretation, normal_style))
        
        # Build the PDF
        doc.build(story)
        
        # Verify the file was created
        if os.path.exists(filepath):
            print(f"PDF report generated successfully at {filepath}")
            print(f"File size: {os.path.getsize(filepath)} bytes")
            return filename  # Return just the filename, not the full path
        else:
            print(f"Error: PDF file not found after generation at {filepath}")
            return None
        
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        return None

def get_score_interpretation(score):
    """Get a concise interpretation of the score."""
    if score >= 4.5:
        return "Outstanding performance with demonstrated mastery"
    elif score >= 3.5:
        return "Strong competency with some areas for enhancement"
    elif score >= 2.5:
        return "Satisfactory with room for development"
    elif score >= 1.5:
        return "Basic understanding, needs improvement"
    else:
        return "Requires significant development"

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