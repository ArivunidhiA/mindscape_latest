from app import create_app, db
from app.models.assessment import Question, ASSESSMENT_QUESTIONS

def seed_questions():
    app = create_app()
    with app.app_context():
        # Clear existing questions
        Question.query.delete()
        
        # Add questions for each assessment type
        for assessment_type, questions in ASSESSMENT_QUESTIONS.items():
            for i, question_text in enumerate(questions):
                # Determine the category based on the question index and assessment type
                if assessment_type == 'lsi':
                    categories = ['humanistic_encouraging', 'affiliative', 'achievement', 'self_actualizing',
                                'approval', 'conventional', 'dependent', 'avoidance',
                                'oppositional', 'power', 'competitive', 'perfectionistic']
                    category = categories[i % len(categories)]
                elif assessment_type == 'oci':
                    categories = ['achievement', 'self_actualizing', 'humanistic_encouraging', 'affiliative']
                    category = categories[i % len(categories)]
                elif assessment_type == 'lpi':
                    categories = ['model_the_way', 'inspire_shared_vision', 'challenge_process',
                                'enable_others_act', 'encourage_heart']
                    category = categories[i % len(categories)]
                else:  # influence
                    categories = ['expert_power', 'referent_power', 'legitimate_power', 'coercive_power']
                    category = categories[i % len(categories)]
                
                question = Question(
                    text=question_text,
                    category=category,
                    assessment_type=assessment_type
                )
                db.session.add(question)
        
        db.session.commit()
        print(f"Database initialized with {Question.query.count()} questions")

if __name__ == '__main__':
    seed_questions() 