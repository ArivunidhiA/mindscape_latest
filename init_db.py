from flask import Flask
from app import db, create_app
from app.models.user import User
from app.models.assessment import Question, ASSESSMENT_QUESTIONS, ASSESSMENT_TYPES
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                name='Admin User',
                age=30,
                is_admin=True
            )
            admin.password = generate_password_hash('admin123')
            db.session.add(admin)
            print("Created admin user")
        
        # Create assessment questions if they don't exist
        existing_questions = Question.query.count()
        if existing_questions == 0:
            # Add questions for each assessment type
            for assessment_type, questions in ASSESSMENT_QUESTIONS.items():
                for i, question_text in enumerate(questions):
                    # Get the category based on the question index and total categories
                    categories = ASSESSMENT_TYPES[assessment_type]['categories']
                    category_index = i % len(categories)
                    category = categories[category_index]
                    
                    question = Question(
                        text=question_text,
                        category=category,
                        assessment_type=assessment_type
                    )
                    db.session.add(question)
            print("Created assessment questions")
        
        db.session.commit()

if __name__ == '__main__':
    init_db() 