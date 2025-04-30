from typing import Dict, List, Tuple

def get_extreme_categories(category_scores: Dict[str, float], num_categories: int = 2) -> Tuple[List[str], List[str]]:
    """Get the highest and lowest scoring categories."""
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    highest = sorted_categories[:num_categories]
    lowest = sorted_categories[-num_categories:]
    return ([h[0] for h in highest], [l[0] for l in lowest])

def format_category_name(category: str) -> str:
    """Format category name for display."""
    return category.replace('_', ' ').title()

def get_lsi_interpretation(category_scores: Dict[str, float]) -> str:
    """Generate interpretation for Life Styles Inventory (LSI) assessment."""
    high_cats, low_cats = get_extreme_categories(category_scores)
    
    interpretations = {
        'self_actualizing': 'strong drive for personal growth and learning',
        'humanistic_encouraging': 'effective at developing and empowering others',
        'affiliative': 'positive interpersonal relationships and collaboration',
        'approval': 'tendency to seek acceptance through agreeing with others',
        'conventional': 'preference for traditional and established approaches',
        'dependent': 'reliance on others for direction and decision-making',
        'avoidance': 'tendency to avoid conflict or difficult situations',
        'oppositional': 'critical thinking but potential resistance to new ideas',
        'power': 'desire for control and influence over situations and others',
        'competitive': 'strong drive to win and outperform others',
        'perfectionistic': 'high standards but possible inflexibility',
        'achievement': 'goal-oriented with focus on personal accomplishment'
    }
    
    # Format strengths and improvements with proper descriptions
    strengths = []
    for cat in high_cats:
        desc = interpretations.get(cat, '')
        if desc:
            strengths.append(f"{format_category_name(cat)} ({desc})")
        else:
            strengths.append(format_category_name(cat))
            
    improvements = []
    for cat in low_cats:
        desc = interpretations.get(cat, '')
        if desc:
            improvements.append(f"{format_category_name(cat)} ({desc})")
        else:
            improvements.append(format_category_name(cat))
    
    return f"Your results show particular strength in {' and '.join(strengths)}. Areas that may benefit from development include {' and '.join(improvements)}. This suggests you have a strong foundation in certain leadership aspects while having opportunities for growth in others."

def get_oci_interpretation(category_scores: Dict[str, float]) -> str:
    """Generate interpretation for Organizational Culture Inventory (OCI) assessment."""
    high_cats, low_cats = get_extreme_categories(category_scores)
    
    interpretations = {
        'achievement': 'emphasis on setting goals and accomplishing tasks',
        'self_actualization': 'creativity and personal growth focus',
        'humanistic_encouraging': 'supportive and developmental environment',
        'affiliative': 'positive workplace relationships and collaboration',
        'approval': 'harmony-seeking organizational behavior',
        'conventional': 'traditional and structured approaches',
        'dependent': 'hierarchical decision-making patterns',
        'avoidance': 'risk-averse organizational behavior',
        'oppositional': 'critical but potentially resistant culture',
        'power': 'control and authority-based interactions',
        'competitive': 'market-driven and results-focused environment',
        'perfectionistic': 'detail-oriented with high standards'
    }
    
    # Format strengths and improvements with proper descriptions
    strengths = []
    for cat in high_cats:
        desc = interpretations.get(cat, '')
        if desc:
            strengths.append(f"{format_category_name(cat)} ({desc})")
        else:
            strengths.append(format_category_name(cat))
            
    improvements = []
    for cat in low_cats:
        desc = interpretations.get(cat, '')
        if desc:
            improvements.append(f"{format_category_name(cat)} ({desc})")
        else:
            improvements.append(format_category_name(cat))
    
    return f"The organizational culture shows strong characteristics of {' and '.join(strengths)}. Areas that might need attention include {' and '.join(improvements)}. This indicates a culture that balances certain organizational values while having room for development in others."

def get_lpi_interpretation(category_scores: Dict[str, float]) -> str:
    """Generate interpretation for Leadership Practices Inventory (LPI) assessment."""
    high_cats, low_cats = get_extreme_categories(category_scores)
    
    interpretations = {
        'model_the_way': 'leading by example and setting clear expectations',
        'inspire_shared_vision': 'creating compelling future possibilities',
        'challenge_process': 'innovation and willingness to take risks',
        'enable_others': 'fostering collaboration and strengthening others',
        'encourage_heart': 'recognizing contributions and celebrating values'
    }
    
    # Format strengths and improvements with proper descriptions
    strengths = []
    for cat in high_cats:
        desc = interpretations.get(cat, '')
        if desc:
            strengths.append(f"{format_category_name(cat)} ({desc})")
        else:
            strengths.append(format_category_name(cat))
            
    improvements = []
    for cat in low_cats:
        desc = interpretations.get(cat, '')
        if desc:
            improvements.append(f"{format_category_name(cat)} ({desc})")
        else:
            improvements.append(format_category_name(cat))
    
    return f"Your leadership style demonstrates excellence in {' and '.join(strengths)}. Consider developing your approach to {' and '.join(improvements)}. This profile suggests you have effective leadership practices in some areas while having potential for growth in others."

def get_influence_interpretation(category_scores: Dict[str, float]) -> str:
    """Generate interpretation for Influence Style Profiler assessment."""
    high_cats, low_cats = get_extreme_categories(category_scores)
    
    interpretations = {
        'referent_power': 'building influence through trust and respect',
        'expert_power': 'leveraging expertise and knowledge',
        'legitimate_power': 'using formal authority and position',
        'coercive_power': 'using pressure or force to influence',
        'reward_power': 'motivating through incentives and recognition'
    }
    
    # Format strengths and improvements with proper descriptions
    strengths = []
    for cat in high_cats:
        desc = interpretations.get(cat, '')
        if desc:
            strengths.append(f"{format_category_name(cat)} ({desc})")
        else:
            strengths.append(format_category_name(cat))
            
    improvements = []
    for cat in low_cats:
        desc = interpretations.get(cat, '')
        if desc:
            improvements.append(f"{format_category_name(cat)} ({desc})")
        else:
            improvements.append(format_category_name(cat))
    
    return f"Your influence style is particularly effective in {' and '.join(strengths)}. You could enhance your impact by developing {' and '.join(improvements)}. This indicates you have strong influence capabilities in certain approaches while having opportunities to expand your influence repertoire."

def get_assessment_interpretation(assessment_type: str, category_scores: Dict[str, float]) -> str:
    """Get interpretation for any assessment type."""
    interpreters = {
        'lsi': get_lsi_interpretation,
        'oci': get_oci_interpretation,
        'lpi': get_lpi_interpretation,
        'influence': get_influence_interpretation
    }
    
    interpreter = interpreters.get(assessment_type)
    if not interpreter:
        return "Assessment type not recognized for interpretation."
        
    return interpreter(category_scores) 