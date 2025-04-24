import click
from flask.cli import with_appcontext
from app import db
from app.models.assessment import Question

@click.command('init-questions')
@with_appcontext
def init_questions_command():
    """Initialize assessment questions."""
    # Delete existing questions
    Question.query.delete()
    
    # Define questions for each category
    questions = [
        # Emotional Intelligence
        {
            'text': 'I can identify and understand my own emotions well.',
            'category': 'emotional_intelligence'
        },
        {
            'text': 'I can effectively manage my emotional reactions in difficult situations.',
            'category': 'emotional_intelligence'
        },
        {
            'text': 'I am good at understanding how others are feeling.',
            'category': 'emotional_intelligence'
        },
        {
            'text': 'I can adapt my communication style based on the emotional state of others.',
            'category': 'emotional_intelligence'
        },
        
        # Leadership
        {
            'text': 'I am comfortable taking initiative and leading group activities.',
            'category': 'leadership'
        },
        {
            'text': 'I can effectively delegate tasks and responsibilities to others.',
            'category': 'leadership'
        },
        {
            'text': 'I am good at motivating and inspiring others.',
            'category': 'leadership'
        },
        {
            'text': 'I can make difficult decisions when necessary.',
            'category': 'leadership'
        },
        
        # Personal Growth
        {
            'text': 'I actively seek opportunities to learn and develop new skills.',
            'category': 'personal_growth'
        },
        {
            'text': 'I am open to feedback and use it to improve myself.',
            'category': 'personal_growth'
        },
        {
            'text': 'I set clear goals for my personal development.',
            'category': 'personal_growth'
        },
        {
            'text': 'I regularly reflect on my experiences to learn from them.',
            'category': 'personal_growth'
        }
    ]
    
    # Add questions to database
    for q in questions:
        question = Question(text=q['text'], category=q['category'])
        db.session.add(question)
    
    db.session.commit()
    click.echo('Assessment questions initialized.') 