from flask import Flask, render_template, request, jsonify, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
import json
import os
from datetime import datetime
from app.utils.pdf_generator import generate_pdf_report
from flask_login import current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Load assessment data
with open('data/assessments.json', 'r') as f:
    assessments = json.load(f)

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Start Assessment')

class AssessmentForm(FlaskForm):
    submit = SubmitField('Submit Assessment')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = UserForm()
    if form.validate_on_submit():
        return render_template('assessments.html', 
                             name=form.name.data, 
                             age=form.age.data,
                             assessments=assessments)
    return render_template('home.html', form=form)

@app.route('/assessment/<assessment_id>', methods=['GET', 'POST'])
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

@app.route('/download/<assessment_id>')
def download_results(assessment_id):
    """Download assessment results as PDF."""
    assessment = next((a for a in assessments if a['id'] == assessment_id), None)
    if not assessment:
        return "Assessment not found", 404
    
    # Get assessment info and scores
    assessment_info = {
        'name': assessment['name'],
        'description': assessment['description'],
        'max_score': 5  # Default max score
    }
    
    # Calculate category scores (example - replace with actual logic)
    category_scores = {}
    responses = request.args.get('responses', '{}')
    responses = json.loads(responses)
    
    # Group questions by category and calculate average scores
    for category in set(q.get('category', 'general') for q in assessment['questions']):
        category_questions = [q for q in assessment['questions'] if q.get('category', 'general') == category]
        if category_questions:
            category_scores[category] = sum(float(responses.get(q['id'], 0)) for q in category_questions) / len(category_questions)
    
    # Create a mock user object if not using authentication
    class MockUser:
        def __init__(self, name):
            self.name = name
    
    user = current_user if hasattr(current_user, 'is_authenticated') else MockUser(request.args.get('name', 'Anonymous'))
    
    # Generate PDF
    pdf_path = generate_pdf_report(assessment, user, assessment_info, category_scores)
    
    # The pdf_path returned is relative to static folder
    full_path = os.path.join(app.root_path, 'static', pdf_path.lstrip('/static/'))
    
    return send_file(
        full_path,
        as_attachment=True,
        download_name=f"{assessment['name']}_Results.pdf"
    )

def calculate_score(assessment_id, responses):
    # This is a placeholder. Implement actual scoring logic based on assessment type
    return sum(int(score) for score in responses.values()) / len(responses)

if __name__ == '__main__':
    app.run(debug=True) 