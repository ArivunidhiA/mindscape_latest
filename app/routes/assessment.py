from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.assessment import Question, Assessment, AssessmentResponse, ASSESSMENT_TYPES
from app import db
from datetime import datetime
from app.utils.pdf_generator import generate_pdf_report
import os
from threading import Thread
import json
from flask import current_app

bp = Blueprint('assessment', __name__)

def get_assessment_type(assessment_type):
    """
    Get assessment type information from ASSESSMENT_TYPES.
    
    Args:
        assessment_type (str): The type of assessment
        
    Returns:
        dict: Assessment type information or None if not found
    """
    return ASSESSMENT_TYPES.get(assessment_type)

class AssessmentForm(FlaskForm):
    """Empty form class for CSRF protection"""
    pass

@bp.route('/')
@login_required
def take_assessment():
    """Display the assessment selection page."""
    return render_template('assessment/select_assessment.html', assessments=ASSESSMENT_TYPES)

@bp.route('/type/<assessment_type>')
@login_required
def assessment_type(assessment_type):
    """Display the questions for a specific assessment type."""
    # Validate assessment type
    if assessment_type not in ASSESSMENT_TYPES:
        flash('Invalid assessment type selected.', 'error')
        return redirect(url_for('assessment.take_assessment'))
    
    # Get questions for the specific assessment type
    questions = Question.query.filter_by(assessment_type=assessment_type).all()
    
    if not questions:
        flash(f'No questions available for the {ASSESSMENT_TYPES[assessment_type]["name"]} assessment.', 'error')
        return redirect(url_for('assessment.take_assessment'))
    
    form = AssessmentForm()
    return render_template('assessment/questions.html', 
                         questions=questions, 
                         form=form, 
                         assessment_type=assessment_type,
                         assessment_info=ASSESSMENT_TYPES[assessment_type])

@bp.route('/submit/<assessment_type>', methods=['POST'])
@login_required
def submit_assessment(assessment_type):
    """Handle assessment submission for a specific type."""
    # Validate assessment type
    if assessment_type not in ASSESSMENT_TYPES:
        flash('Invalid assessment type selected.', 'error')
        return redirect(url_for('assessment.take_assessment'))
    
    form = AssessmentForm()
    if not form.validate_on_submit():
        flash('Invalid form submission. Please try again.', 'error')
        return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))
    
    if not request.form:
        flash('No responses were submitted.', 'error')
        return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))
    
    # Create new assessment
    assessment = Assessment(
        user_id=current_user.id,
        assessment_type=assessment_type,
        completed_at=datetime.utcnow()
    )
    db.session.add(assessment)
    db.session.flush()  # Get the assessment ID
    
    # Process each question response
    questions = Question.query.filter_by(assessment_type=assessment_type).all()
    for question in questions:
        response_key = f'question_{question.id}'
        if response_key not in request.form:
            flash('Please answer all questions.', 'error')
            return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))
        
        try:
            score = int(request.form[response_key])
            max_score = ASSESSMENT_TYPES[assessment_type]['max_score']
            if not 1 <= score <= max_score:
                raise ValueError
        except ValueError:
            flash('Invalid response value provided.', 'error')
            return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))
        
        # Save the response
        response = AssessmentResponse(
            assessment_id=assessment.id,
            question_id=question.id,
            score=score
        )
        db.session.add(response)
    
    try:
        db.session.commit()
        flash('Assessment completed successfully!', 'success')
        return redirect(url_for('assessment.results', assessment_id=assessment.id))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while saving your responses. Please try again.', 'error')
        return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))

def generate_pdf_async(assessment, user, assessment_info, category_scores):
    """Generate PDF report in a background thread."""
    try:
        # Create static/pdfs directory if it doesn't exist
        pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generate the PDF report
        pdf_path = generate_pdf_report(assessment, current_user, assessment_info, category_scores)
        
        if pdf_path:
            # Verify the file exists
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', pdf_path.lstrip('/'))
            if not os.path.exists(full_path):
                return None
            return pdf_path
    except Exception as e:
        print(f"Error in async PDF generation: {str(e)}")
        return None

@bp.route('/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    """Display assessment results and generate PDF report."""
    try:
        # Get assessment and verify user has permission to view it
        assessment = Assessment.query.get_or_404(assessment_id)
        if assessment.user_id != current_user.id:
            flash('You do not have permission to view these results.', 'error')
            return redirect(url_for('assessment.history'))

        # Get assessment type info
        assessment_info = get_assessment_type(assessment.assessment_type)
        if not assessment_info:
            flash('Invalid assessment type.', 'error')
            return redirect(url_for('assessment.history'))

        # Calculate category scores
        category_scores = {}
        category_counts = {}
        
        # Initialize scores for all categories
        for category in assessment_info['categories']:
            category_scores[category] = 0
            category_counts[category] = 0
        
        # Sum up scores for each category
        for response in assessment.responses:
            category = response.question.category
            category_scores[category] += response.score
            category_counts[category] += 1
        
        # Calculate average for each category
        for category in category_scores:
            if category_counts[category] > 0:
                category_scores[category] = round(
                    category_scores[category] / category_counts[category],
                    2
                )

        # Generate PDF report
        pdf_path = generate_pdf_report(
            assessment=assessment,
            user=current_user,
            assessment_info=assessment_info,
            category_scores=category_scores
        )
        
        if pdf_path:
            # Verify the PDF file exists
            pdf_file = os.path.join(current_app.root_path, pdf_path.lstrip('/'))
            if not os.path.exists(pdf_file):
                print(f"PDF file not found at {pdf_file}")
                pdf_path = None
            else:
                # Get just the filename for the download route
                pdf_path = os.path.basename(pdf_file)

        return render_template(
            'assessment/results.html',
            assessment=assessment,
            category_scores=category_scores,
            assessment_info=assessment_info,
            pdf_path=pdf_path
        )

    except Exception as e:
        print(f"Error in results route: {str(e)}")
        flash('An error occurred while generating the results.', 'error')
        return redirect(url_for('assessment.history'))

@bp.route('/api/pdf_status/<int:assessment_id>')
@login_required
def check_pdf_status(assessment_id):
    """Check if PDF has been generated for the assessment."""
    try:
        # Look for the PDF file
        pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'pdfs')
        pattern = f"assessment_report_{assessment_id}_*.pdf"
        matches = []
        for filename in os.listdir(pdf_dir):
            if filename.startswith(f"assessment_report_{assessment_id}_") and filename.endswith(".pdf"):
                matches.append(filename)
        
        if matches:
            # Get the most recent PDF
            latest_pdf = sorted(matches)[-1]
            return jsonify({
                'status': 'ready',
                'pdf_path': f'/static/pdfs/{latest_pdf}'
            })
        
        return jsonify({'status': 'generating'})
        
    except Exception as e:
        print(f"Error checking PDF status: {str(e)}")
        return jsonify({'status': 'error'})

@bp.route('/history')
@login_required
def history():
    """Display user's assessment history."""
    assessments = Assessment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assessment.completed_at.desc()).all()
    
    return render_template('assessment/history.html', 
                         assessments=assessments,
                         assessment_types=ASSESSMENT_TYPES)

@bp.route('/api/results/<int:assessment_id>')
@login_required
def api_results(assessment_id):
    """API endpoint for getting assessment results data for charts."""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Ensure the user can only view their own results
    if assessment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get assessment type info
    assessment_info = ASSESSMENT_TYPES.get(assessment.assessment_type)
    if not assessment_info:
        return jsonify({'error': 'Invalid assessment type'}), 400
    
    # Calculate scores for each category
    category_scores = {}
    for category in assessment_info['categories']:
        score = assessment.get_category_score(category)
        category_scores[category] = score
    
    return jsonify({
        'type': assessment_info.get('visualization', 'radar'),  # Default to radar if not specified
        'categories': list(category_scores.keys()),
        'scores': list(category_scores.values()),
        'max_score': assessment_info['max_score']
    })

@bp.route('/download/<path:filename>')
@login_required
def download_pdf(filename):
    """Download PDF report."""
    try:
        # Security check - ensure filename is a PDF
        if not filename.endswith('.pdf'):
            flash('Invalid file request.', 'error')
            return redirect(url_for('assessment.history'))
            
        # Get full path
        pdf_dir = os.path.join(current_app.root_path, 'static', 'pdfs')
        file_path = os.path.join(pdf_dir, filename)
        
        # Security check - ensure file exists and is within pdfs directory
        if not os.path.exists(file_path) or not os.path.commonpath([file_path, pdf_dir]) == pdf_dir:
            flash('File not found.', 'error')
            return redirect(url_for('assessment.history'))
            
        # Send the file
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error downloading PDF: {str(e)}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('assessment.history')) 