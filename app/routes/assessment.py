from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.assessment import Question, Assessment, AssessmentResponse, ASSESSMENT_TYPES
from app import db
from datetime import datetime
from app.utils.pdf_generator import generate_pdf_report
from app.utils.interpretation import get_assessment_interpretation
import os
from threading import Thread
import json
from flask import current_app
import logging
from pytz import timezone

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
    logging.info(f"Requested assessment type: {assessment_type}")
    
    # Validate assessment type
    if assessment_type not in ASSESSMENT_TYPES:
        flash('Invalid assessment type selected.', 'error')
        return redirect(url_for('assessment.take_assessment'))
    
    try:
        # Get questions for the specific assessment type in a single query
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
    except Exception as e:
        logging.error(f"Error in assessment_type route: {str(e)}")
        flash('An error occurred while loading the assessment.', 'error')
        return redirect(url_for('assessment.take_assessment'))

@bp.route('/submit/<assessment_type>', methods=['POST'])
@login_required
def submit_assessment(assessment_type):
    """Handle assessment submission for a specific type."""
    logging.info(f"Processing assessment submission for type: {assessment_type}")
    
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
    
    try:
        # Create new assessment
        assessment = Assessment(
            user_id=current_user.id,
            assessment_type=assessment_type,
            completed_at=datetime.utcnow()
        )
        db.session.add(assessment)
        db.session.flush()
        
        # Get all questions in a single query
        questions = Question.query.filter_by(assessment_type=assessment_type).all()
        
        # Process responses in a single transaction
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
                
                response = AssessmentResponse(
                    assessment_id=assessment.id,
                    question_id=question.id,
                    score=score
                )
                db.session.add(response)
            except ValueError:
                flash('Invalid response value provided.', 'error')
                return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))
        
        db.session.commit()
        flash('Assessment completed successfully!', 'success')
        return redirect(url_for('assessment.results', assessment_id=assessment.id))
        
    except Exception as e:
        logging.error(f"Error in submit_assessment: {str(e)}")
        db.session.rollback()
        flash('An error occurred while saving your responses. Please try again.', 'error')
        return redirect(url_for('assessment.assessment_type', assessment_type=assessment_type))

def generate_pdf_async(assessment, user, assessment_info, category_scores):
    """Generate PDF report in a background thread."""
    try:
        # Generate the PDF report
        pdf_path = generate_pdf_report(assessment, user, assessment_info, category_scores)
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

        # Generate interpretation
        interpretation = get_assessment_interpretation(assessment.assessment_type, category_scores)

        # Generate PDF report
        pdf_filename = None
        try:
            pdf_filename = generate_pdf_report(
                assessment=assessment,
                user=current_user,
                assessment_info=assessment_info,
                category_scores=category_scores,
                interpretation=interpretation
            )
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

        return render_template(
            'assessment/results.html',
            assessment=assessment,
            assessment_info=assessment_info,
            category_scores=category_scores,
            interpretation=interpretation,
            pdf_filename=pdf_filename
        )

    except Exception as e:
        print(f"Error displaying results: {str(e)}")
        flash('An error occurred while displaying the results.', 'error')
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
    
    # Convert UTC times to Eastern Time (EST/EDT)
    local_tz = timezone('America/New_York')
    for assessment in assessments:
        if assessment.completed_at.tzinfo is None:
            assessment.completed_at = timezone('UTC').localize(assessment.completed_at)
        assessment.completed_at = assessment.completed_at.astimezone(local_tz)
    
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
    """Download a PDF report."""
    try:
        # Security check: ensure filename only contains safe characters
        if not filename or '..' in filename:
            flash('Invalid filename.', 'error')
            return redirect(url_for('assessment.history'))
            
        # Construct the full path
        pdf_dir = os.path.join(current_app.root_path, 'static', 'pdfs')
        file_path = os.path.join(pdf_dir, filename)
        
        # Debug logging
        print(f"Attempting to download PDF: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        # Verify file exists and is in the correct directory
        if not os.path.exists(file_path):
            print(f"PDF file not found at path: {file_path}")
            flash('PDF file not found.', 'error')
            return redirect(url_for('assessment.history'))
            
        if not os.path.commonpath([file_path, pdf_dir]) == pdf_dir:
            print(f"Security check failed: file path {file_path} is outside pdf_dir {pdf_dir}")
            flash('Invalid file path.', 'error')
            return redirect(url_for('assessment.history'))
            
        # Get the assessment ID from the filename
        try:
            # Handle both old and new filename formats
            if '_' in filename:
                if filename.startswith('assessment_report_'):
                    assessment_id = int(filename.split('_')[2])
                else:
                    # New format: LSI_28Apr25.pdf
                    return send_file(
                        file_path,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=filename
                    )
                    
                assessment = Assessment.query.get_or_404(assessment_id)
                
                # Check if user has permission to download this PDF
                if assessment.user_id != current_user.id:
                    flash('You do not have permission to download this file.', 'error')
                    return redirect(url_for('assessment.history'))
            
        except (ValueError, IndexError) as e:
            print(f"Error parsing filename: {str(e)}")
            # Don't redirect - try to send the file anyway if it exists
            pass
            
        print(f"Sending file: {file_path}")
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error downloading PDF: {str(e)}")
        flash('An error occurred while downloading the PDF.', 'error')
        return redirect(url_for('assessment.history')) 