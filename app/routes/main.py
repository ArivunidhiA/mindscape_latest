from flask import Blueprint, render_template, request, jsonify, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import json
import os
from datetime import datetime
from app.utils.pdf_generator import generate_pdf_report
from flask_login import current_user

bp = Blueprint('main', __name__)

# Load assessment data
with open('data/assessments.json', 'r') as f:
    assessments = json.load(f)

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Start Assessment')

class AssessmentForm(FlaskForm):
    submit = SubmitField('Submit Assessment')

@bp.route('/', methods=['GET', 'POST'])
def home():
    form = UserForm()
    if form.validate_on_submit():
        return render_template('assessments.html', 
                            name=form.name.data, 
                            age=form.age.data,
                            assessments=assessments)
    return render_template('home.html', form=form)

@bp.route('/assessment/<assessment_id>', methods=['GET', 'POST'])
def assessment(assessment_id):
    assessment = next((a for a in assessments if a['id'] == assessment_id), None)
    if not assessment:
        return "Assessment not found", 404
    
    if request.method == 'POST':
        responses = request.form.to_dict()
        score = calculate_score(assessment_id, responses)
        return render_template('results.html', 
                            assessment=assessment,
                            score=score,
                            name=request.args.get('name'),
                            age=request.args.get('age'))
    
    return render_template('assessment.html', 
                        assessment=assessment,
                        name=request.args.get('name'),
                        age=request.args.get('age'))

@bp.route('/download/<assessment_id>')
def download_results(assessment_id):
    assessment = next((a for a in assessments if a['id'] == assessment_id), None)
    if not assessment:
        return "Assessment not found", 404
    
    assessment_info = {
        'name': assessment['name'],
        'description': assessment['description'],
        'max_score': 5
    }
    
    category_scores = {}
    responses = request.args.get('responses', '{}')
    responses = json.loads(responses)
    
    for category in set(q.get('category', 'general') for q in assessment['questions']):
        category_questions = [q for q in assessment['questions'] if q.get('category', 'general') == category]
        if category_questions:
            category_scores[category] = sum(float(responses.get(q['id'], 0)) for q in category_questions) / len(category_questions)
    
    class MockUser:
        def __init__(self, name):
            self.name = name
    
    user = current_user if hasattr(current_user, 'is_authenticated') else MockUser(request.args.get('name', 'Anonymous'))
    
    pdf_path = generate_pdf_report(assessment, user, assessment_info, category_scores)
    full_path = os.path.join(current_app.root_path, 'static', pdf_path.lstrip('/static/'))
    
    return send_file(
        full_path,
        as_attachment=True,
        download_name=f"{assessment['name']}_Results.pdf"
    )

def calculate_score(assessment_id, responses):
    return sum(int(score) for score in responses.values()) / len(responses) 