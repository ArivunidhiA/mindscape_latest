from flask import Flask
from app import db, create_app
from app.models.user import User
from app.models.assessment import Question, ASSESSMENT_QUESTIONS, ASSESSMENT_TYPES
from werkzeug.security import generate_password_hash
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        print("Database tables recreated")
        
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
        
        # Add questions for each assessment type
        for assessment_type, questions in ASSESSMENT_QUESTIONS.items():
            print(f"\nAdding questions for {assessment_type} assessment:")
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
                print(f"Added question {i+1}: {question_text[:50]}...")
        
        try:
            db.session.commit()
            print("\nSuccessfully seeded all questions into the database")
            
            # Verify the questions were added
            for assessment_type in ASSESSMENT_QUESTIONS.keys():
                count = Question.query.filter_by(assessment_type=assessment_type).count()
                print(f"Total questions for {assessment_type}: {count}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding questions: {str(e)}")
            raise

if __name__ == '__main__':
    init_db() 