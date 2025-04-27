import click
from flask.cli import with_appcontext
from app import db
from app.models.assessment import Question, ASSESSMENT_QUESTIONS, ASSESSMENT_TYPES

def register_commands(app):
    app.cli.add_command(seed_questions)

@click.command('seed-questions')
@with_appcontext
def seed_questions():
    """Seed the database with assessment questions."""
    try:
        # Check if questions already exist
        existing_count = Question.query.count()
        if existing_count > 0:
            click.echo('Questions already exist in the database. Skipping seeding.')
            return

        # Add questions for each assessment type
        for assessment_type, questions in ASSESSMENT_QUESTIONS.items():
            categories = ASSESSMENT_TYPES[assessment_type]['categories']
            category_count = len(categories)
            
            for i, question_text in enumerate(questions):
                # Distribute questions evenly across categories
                category = categories[i % category_count]
                
                question = Question(
                    text=question_text,
                    category=category,
                    assessment_type=assessment_type
                )
                db.session.add(question)
        
        db.session.commit()
        click.echo('Successfully seeded assessment questions.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error seeding questions: {str(e)}')
        raise 