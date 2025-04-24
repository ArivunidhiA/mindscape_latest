from flask import Flask, render_template, request, jsonify, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

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
    assessment = next((a for a in assessments if a['id'] == assessment_id), None)
    if not assessment:
        return "Assessment not found", 404
    
    name = request.args.get('name')
    age = request.args.get('age')
    score = request.args.get('score')
    
    # Create PDF
    filename = f"results_{assessment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(f"{assessment['name']} Assessment Results", title_style))
    
    # Add user info
    story.append(Paragraph(f"Name: {name}", styles['Normal']))
    story.append(Paragraph(f"Age: {age}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Add score
    story.append(Paragraph(f"Score: {score}", styles['Heading2']))
    
    # Build PDF
    doc.build(story)
    
    return send_file(filename, as_attachment=True)

def calculate_score(assessment_id, responses):
    # This is a placeholder. Implement actual scoring logic based on assessment type
    return sum(int(score) for score in responses.values()) / len(responses)

if __name__ == '__main__':
    app.run(debug=True) 