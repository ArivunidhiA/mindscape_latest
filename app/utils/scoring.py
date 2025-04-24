def calculate_lsi_scores(responses):
    """Calculate Life Styles Inventory scores"""
    styles = {
        'humanistic': [0, 1, 2, 3],
        'affiliative': [4, 5, 6, 7],
        'achievement': [8, 9, 10, 11],
        'self_actualizing': [12, 13, 14, 15],
        'approval': [16, 17, 18, 19],
        'conventional': [20, 21, 22, 23],
        'dependent': [24, 25, 26, 27],
        'avoidance': [28, 29, 30, 31],
        'oppositional': [32, 33, 34, 35],
        'power': [36, 37, 38, 39],
        'competitive': [40, 41, 42, 43],
        'perfectionistic': [44, 45, 46, 47]
    }
    
    raw_scores = {}
    for style, questions in styles.items():
        style_scores = [responses.get(str(q), 0) for q in questions]
        raw_scores[style] = sum(style_scores) / len(style_scores)
    
    return raw_scores

def calculate_oci_scores(responses):
    """Calculate Organizational Culture Inventory scores"""
    norms = {
        'constructive': {
            'achievement': [0, 1, 2, 3, 4],
            'self_actualizing': [5, 6, 7, 8, 9],
            'humanistic': [10, 11, 12, 13, 14],
            'affiliative': [15, 16, 17, 18, 19]
        },
        'passive_defensive': {
            'approval': [20, 21, 22, 23, 24],
            'conventional': [25, 26, 27, 28, 29],
            'dependent': [30, 31, 32, 33, 34],
            'avoidance': [35, 36, 37, 38, 39]
        },
        'aggressive_defensive': {
            'oppositional': [40, 41, 42, 43, 44],
            'power': [45, 46, 47, 48, 49]
        }
    }
    
    scores = {}
    for category, styles in norms.items():
        category_scores = {}
        for style, indices in styles.items():
            style_scores = [responses.get(str(i), 0) for i in indices]
            category_scores[style] = sum(style_scores) / len(style_scores)
        scores[category] = category_scores
    
    return scores

def calculate_lpi_scores(responses):
    """Calculate Leadership Practices Inventory scores"""
    practices = {
        'model_way': [0, 1, 2, 3, 4, 5],
        'inspire_vision': [6, 7, 8, 9, 10, 11],
        'challenge_process': [12, 13, 14, 15, 16, 17],
        'enable_others': [18, 19, 20, 21, 22, 23],
        'encourage_heart': [24, 25, 26, 27, 28, 29]
    }
    
    scores = {}
    for practice, indices in practices.items():
        practice_scores = [responses.get(str(i), 0) for i in indices]
        scores[practice] = {
            'raw_score': sum(practice_scores),
            'average': sum(practice_scores) / len(practice_scores)
        }
    
    return scores

def calculate_influence_scores(responses):
    """Calculate Influence Style Profiler scores"""
    power_types = {
        'expert': list(range(0, 8)),
        'referent': list(range(8, 16)),
        'legitimate': list(range(16, 24)),
        'coercive': list(range(24, 32))
    }
    
    scores = {}
    for power_type, indices in power_types.items():
        type_scores = [responses.get(str(i), 0) for i in indices]
        scores[power_type] = sum(type_scores) / len(type_scores)
    
    return scores

def calculate_scores(data):
    """
    Calculate scores for each dimension based on user responses.
    
    Args:
        data (dict): Dictionary containing user responses for each question
        
    Returns:
        dict: Dictionary containing scores for each dimension
    """
    # Initialize scores for each dimension
    scores = {
        'leadership': 0,
        'teamwork': 0,
        'communication': 0,
        'problem_solving': 0,
        'adaptability': 0
    }
    
    # Question mapping to dimensions
    question_dimensions = {
        'q1': 'leadership',
        'q2': 'teamwork',
        'q3': 'communication',
        'q4': 'problem_solving',
        'q5': 'adaptability',
        'q6': 'leadership',
        'q7': 'teamwork',
        'q8': 'communication',
        'q9': 'problem_solving',
        'q10': 'adaptability'
    }
    
    # Calculate scores
    for question_id, response in data.items():
        if question_id in question_dimensions:
            dimension = question_dimensions[question_id]
            # Convert response to score (assuming responses are 1-5)
            score = int(response)
            scores[dimension] += score
    
    # Calculate average scores for each dimension
    for dimension in scores:
        # Each dimension has 2 questions
        scores[dimension] = scores[dimension] / 2
    
    return scores 