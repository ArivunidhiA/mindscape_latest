from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.assessment import Assessment, ASSESSMENT_QUESTIONS
from app.utils.scoring import calculate_scores
from app.utils.pdf_generator import generate_pdf_report

assessment_bp = Blueprint('assessment', __name__)

SECTIONS = ['emotional_intelligence', 'leadership', 'personal_growth']
SECTION_TITLES = {
    'emotional_intelligence': 'Emotional Intelligence Assessment',
    'leadership': 'Leadership Skills Assessment',
    'personal_growth': 'Personal Growth Assessment'
}

@assessment_bp.route('/assessment')
@login_required
def take_assessment():
    # Check if there's an ongoing assessment
    ongoing = Assessment.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).first()
    
    if ongoing:
        # Resume from the last section
        next_section = session.get('current_section', SECTIONS[0])
        return redirect(url_for('assessment.questions', section=next_section))
    
    # Create new assessment
    assessment = Assessment(user_id=current_user.id)
    db.session.add(assessment)
    db.session.commit()
    
    # Store assessment ID in session
    session['assessment_id'] = assessment.id
    session['current_section'] = SECTIONS[0]
    
    return redirect(url_for('assessment.questions', section=SECTIONS[0]))

@assessment_bp.route('/assessment/questions/<section>', methods=['GET', 'POST'])
@login_required
def questions(section):
    if section not in SECTIONS:
        return redirect(url_for('assessment.take_assessment'))
    
    current_section_index = SECTIONS.index(section)
    previous_section = SECTIONS[current_section_index - 1] if current_section_index > 0 else None
    
    return render_template(
        'assessment/questions.html',
        questions=ASSESSMENT_QUESTIONS[section],
        section_title=SECTION_TITLES[section],
        current_section=section,
        current_section_index=current_section_index,
        previous_section=previous_section
    )

@assessment_bp.route('/assessment/submit/<section>', methods=['POST'])
@login_required
def submit_section(section):
    if section not in SECTIONS:
        return redirect(url_for('assessment.take_assessment'))
    
    assessment_id = session.get('assessment_id')
    if not assessment_id:
        return redirect(url_for('assessment.take_assessment'))
    
    assessment = Assessment.query.get(assessment_id)
    if not assessment or assessment.user_id != current_user.id:
        return redirect(url_for('assessment.take_assessment'))
    
    # Get responses for current section
    responses = assessment.responses or {}
    section_responses = {
        question['id']: int(request.form.get(question['id'], 1))
        for question in ASSESSMENT_QUESTIONS[section]
    }
    responses[section] = section_responses
    assessment.responses = responses
    
    # Calculate section score
    section_score = sum(section_responses.values()) / len(section_responses)
    if section == 'emotional_intelligence':
        assessment.emotional_intelligence_score = section_score
    elif section == 'leadership':
        assessment.leadership_score = section_score
    else:
        assessment.personal_growth_score = section_score
    
    current_section_index = SECTIONS.index(section)
    if current_section_index == len(SECTIONS) - 1:
        # Last section completed
        assessment.completed = True
        db.session.commit()
        return redirect(url_for('assessment.results', assessment_id=assessment_id))
    
    # Move to next section
    next_section = SECTIONS[current_section_index + 1]
    session['current_section'] = next_section
    db.session.commit()
    
    return redirect(url_for('assessment.questions', section=next_section))

@assessment_bp.route('/assessment/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        flash('You do not have permission to view these results.')
        return redirect(url_for('main.index'))
    
    return render_template('assessment/results.html', assessment=assessment)

@assessment_bp.route('/assessment/history')
@login_required
def history():
    assessments = Assessment.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(Assessment.timestamp.desc()).all()
    
    return render_template('assessment/history.html', assessments=assessments)

@assessment_bp.route('/assessment', methods=['GET', 'POST'])
@login_required
def take_assessment_post():
    if request.method == 'POST':
        data = request.get_json()
        scores = calculate_scores(data)
        
        assessment = Assessment(
            user_id=current_user.id,
            scores=scores
        )
        db.session.add(assessment)
        db.session.commit()
        
        # Generate PDF report
        pdf_path = generate_pdf_report(assessment, current_user)
        
        return jsonify({
            'success': True,
            'message': 'Assessment completed successfully',
            'pdf_path': pdf_path
        })
    
    return render_template('assessment/take.html', title='Take Assessment')

@assessment_bp.route('/results/<int:assessment_id>')
@login_required
def view_result(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        flash('You do not have permission to view this assessment')
        return redirect(url_for('assessment.view_results'))
    return render_template('assessment/result_detail.html', title='Assessment Result', assessment=assessment) 