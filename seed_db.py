from app import create_app, db
from app.models.assessment import Question
from app.cli import seed_questions
from config import DevelopmentConfig

def seed_database():
    app = create_app(DevelopmentConfig)
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if questions need to be seeded
        if Question.query.count() == 0:
            seed_questions()
            print("Database seeded with initial questions.")
        else:
            print("Questions already exist in the database.")

if __name__ == '__main__':
    seed_database() 