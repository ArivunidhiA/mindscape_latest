from datetime import datetime
from app import db
from sqlalchemy import func

class Question(db.Model):
    """Assessment question model."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # emotional_intelligence, leadership, personal_growth
    assessment_type = db.Column(db.String(50), nullable=False)  # Type of assessment this question belongs to
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_scale_label(self, value):
        """Return the label for a given scale value."""
        return ASSESSMENT_TYPES[self.assessment_type]['scale'].get(value, str(value))

class Assessment(db.Model):
    """User assessment model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # Type of assessment taken
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('AssessmentResponse', backref='assessment', lazy=True)
    
    def get_category_score(self, category):
        """Calculate the average score for a specific category."""
        category_responses = [r for r in self.responses if r.question.category == category]
        if not category_responses:
            return 0.0
        return sum(r.score for r in category_responses) / len(category_responses)
        
    def get_all_category_scores(self):
        """Calculate scores for all categories in this assessment type."""
        scores = {}
        categories = ASSESSMENT_TYPES[self.assessment_type]['categories']
        for category in categories:
            scores[category] = self.get_category_score(category)
        return scores

class AssessmentResponse(db.Model):
    """Individual response to an assessment question."""
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref=db.backref('responses', lazy=True))

# Define assessment types and their details
ASSESSMENT_TYPES = {
    'lsi': {
        'name': 'Life Styles Inventory (LSI)',
        'description': 'Evaluates thinking patterns and behavioral styles that impact leadership effectiveness.',
        'duration': 12,
        'categories': [
            'humanistic_encouraging', 'affiliative', 'achievement', 'self_actualizing',
            'approval', 'conventional', 'dependent', 'avoidance',
            'oppositional', 'power', 'competitive', 'perfectionistic'
        ],
        'scale': {
            1: 'Never',
            2: 'Rarely',
            3: 'Sometimes',
            4: 'Often',
            5: 'Always'
        },
        'visualization': 'radar',  # Type of chart to use for results
        'max_score': 5  # Maximum score per question
    },
    'oci': {
        'name': 'Organizational Culture Inventory (OCI)',
        'description': 'Identifies behavioral norms and cultural expectations within organizations.',
        'duration': 15,
        'categories': [
            'achievement', 'self_actualizing', 'humanistic_encouraging', 'affiliative',
            'approval', 'conventional', 'dependent', 'avoidance',
            'oppositional', 'power', 'competitive', 'perfectionistic'
        ],
        'scale': {
            1: 'Strongly Disagree',
            2: 'Disagree',
            3: 'Neutral',
            4: 'Agree',
            5: 'Strongly Agree'
        },
        'visualization': 'circumplex',  # Type of chart to use for results
        'max_score': 5
    },
    'lpi': {
        'name': 'Leadership Practices Inventory (LPI)',
        'description': 'Measures frequency of key leadership behaviors across five core practices.',
        'duration': 10,
        'categories': [
            'model_the_way', 'inspire_shared_vision', 'challenge_process',
            'enable_others_act', 'encourage_heart'
        ],
        'scale': {
            1: '1 (Almost Never)',
            2: '2',
            3: '3',
            4: '4',
            5: '5 (Occasionally)',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10 (Almost Always)'
        },
        'visualization': 'pentagon',  # Type of chart to use for results
        'max_score': 10
    },
    'influence': {
        'name': 'Influence Style Profiler',
        'description': 'Analyzes personal power and influence strategies in leadership situations.',
        'duration': 10,
        'categories': [
            'expert_power', 'referent_power', 'legitimate_power', 'coercive_power'
        ],
        'scale': {
            1: 'Strongly Disagree',
            2: 'Disagree',
            3: 'Neutral',
            4: 'Agree',
            5: 'Strongly Agree'
        },
        'visualization': 'polar',  # Type of chart to use for results
        'max_score': 5
    }
}

# Define questions for each assessment type
ASSESSMENT_QUESTIONS = {
    'lsi': [
        "I support and encourage others in their development",
        "I help others find meaning in their work",
        "I show genuine concern for others' well-being",
        "I empower others to take initiative",
        "I build strong relationships with colleagues",
        "I promote teamwork and collaboration",
        "I create a positive work environment",
        "I foster open communication",
        "I set challenging but realistic goals",
        "I pursue excellence in my work",
        "I take initiative to accomplish tasks",
        "I measure my performance against high standards",
        "I seek opportunities for personal growth",
        "I think creatively and innovatively",
        "I enjoy challenging tasks",
        "I maintain my integrity in all situations",
        "I seek others' approval before acting",
        "I try to please everyone",
        "I worry about others' opinions",
        "I avoid confrontation",
        "I follow established procedures",
        "I conform to expected norms",
        "I play it safe",
        "I stick to traditional approaches",
        "I rely on others for direction",
        "I hesitate to act independently",
        "I seek guidance frequently",
        "I defer to others' judgments",
        "I avoid taking responsibility",
        "I postpone difficult decisions",
        "I withdraw from challenging situations",
        "I hesitate to take action",
        "I point out flaws in others' ideas",
        "I tend to disagree with others",
        "I criticize new ideas",
        "I resist others' suggestions",
        "I seek to control situations",
        "I assert my authority",
        "I demand compliance from others",
        "I use my position to influence others"
    ],
    'oci': [
        "Set challenging goals",
        "Pursue a standard of excellence",
        "Work for the sense of accomplishment",
        "Think ahead and plan",
        "Take on challenging tasks",
        "Show concern for people",
        "Deal with others in a friendly way",
        "Be supportive of others",
        "Help others grow and develop",
        "Cooperate with others",
        "Be a good listener",
        "Encourage others",
        "Share feelings and thoughts",
        "Be tactful",
        "Use good human relations skills"
    ],
    'lpi': [
        "I set a personal example of what I expect from others",
        "I follow through on promises and commitments",
        "I ask for feedback on how my actions affect others' performance",
        "I build consensus around organization's values",
        "I ensure that people adhere to agreed-upon standards",
        "I create opportunities for people to experiment and take risks",
        "I describe a compelling image of the future",
        "I appeal to others to share dreams of the future",
        "I show others how their interests can be realized",
        "I look ahead and communicate about future trends",
        "I actively listen to diverse points of view",
        "I treat others with dignity and respect",
        "I give people choice about how to do their work",
        "I foster cooperative relationships",
        "I create an atmosphere of mutual trust"
    ],
    'influence': [
        "I rely on my expertise to influence decisions",
        "I use my knowledge to guide others",
        "I demonstrate competence in my field",
        "I build trust through personal relationships",
        "I inspire others through my actions",
        "I lead by example",
        "I use my position to direct others",
        "I rely on formal authority",
        "I enforce organizational policies",
        "I implement disciplinary measures when needed",
        "I use rewards to motivate others",
        "I provide consequences for non-compliance"
    ]
}

class AssessmentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    responses = db.Column(db.JSON)  # Store user responses as JSON
    score = db.Column(db.Float)
    percentile = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional fields for different assessment types
    style_classification = db.Column(db.JSON)  # For LSI
    cultural_alignment = db.Column(db.JSON)  # For OCI
    practice_scores = db.Column(db.JSON)  # For LPI
    power_distribution = db.Column(db.JSON)  # For Influence Style Profiler
    
    def __repr__(self):
        return f'<AssessmentResult {self.id}>' 