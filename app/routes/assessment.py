from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.assessment import Question, Assessment, AssessmentResponse, ASSESSMENT_TYPES
from app import db
from datetime import datetime

bp = Blueprint('assessment', __name__)

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

@bp.route('/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    """Display assessment results."""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Ensure the user can only view their own results
    if assessment.user_id != current_user.id:
        flash('You do not have permission to view these results.', 'error')
        return redirect(url_for('main.index'))
    
    # Get assessment type info
    assessment_info = ASSESSMENT_TYPES.get(assessment.assessment_type)
    if not assessment_info:
        flash('Invalid assessment type.', 'error')
        return redirect(url_for('assessment.history'))
    
    # Calculate scores for each category
    category_scores = {}
    for category in assessment_info['categories']:
        score = assessment.get_category_score(category)
        category_scores[category] = score
    
    return render_template('assessment/results.html', 
                         assessment=assessment,
                         assessment_info=assessment_info,
                         category_scores=category_scores)

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
        'type': assessment_info['visualization'],
        'categories': assessment_info['categories'],
        'scores': list(category_scores.values()),
        'max_score': assessment_info['max_score']
    }) 