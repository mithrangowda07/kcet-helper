from colleges.models import Branch, Cutoff, Category
from django.db.models import Q


def get_recommendations(kcet_rank, category=None, year='2025', round='r1'):
    """
    Get recommended branches based on KCET rank.
    
    Args:
        kcet_rank: Student's KCET rank
        category: Category (e.g., 'GM', 'SC', 'ST', etc.)
        year: Year to check (default '2025')
        round: Round to check (default 'r1')
    
    Returns:
        List of recommended branches with cutoff information
    """
    cutoff_field = f'cutoff_{year}_{round}'
    
    # Get all cutoffs for the specified year and round
    cutoffs = Cutoff.objects.select_related('unique_key__college', 'unique_key__cluster').all()
    
    # If category is provided, get fall_back categories
    valid_categories = set()
    if category:
        try:
            cat_obj = Category.objects.get(category=category)
            # Parse fall_back: "1R,1G,GM" -> ["1R", "1G", "GM"]
            fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',')]
            valid_categories = set(fall_back_list)
        except Category.DoesNotExist:
            valid_categories = {category}
    
    recommendations = []
    
    for cutoff in cutoffs:
        # Filter by category if provided (including fall_back)
        if category:
            if cutoff.category not in valid_categories:
                continue
        
        # Get the cutoff value for the specified year and round
        cutoff_value = getattr(cutoff, cutoff_field, None)
        
        if not cutoff_value or cutoff_value == '':
            continue
        
        try:
            # Try to parse as integer (closing rank)
            closing_rank = int(cutoff_value)
            
            # Check if student rank is within range
            # We consider a branch eligible if student rank <= closing rank
            if kcet_rank <= closing_rank:
                distance = closing_rank - kcet_rank
                
                # Get opening rank (could be from previous rounds or same round)
                # For simplicity, we'll use the same value or try to find opening rank
                opening_rank = closing_rank  # Default, can be improved
                
                # Try to find opening rank from previous rounds
                for prev_round in ['r1', 'r2', 'r3']:
                    prev_field = f'cutoff_{year}_{prev_round}'
                    prev_value = getattr(cutoff, prev_field, None)
                    if prev_value:
                        try:
                            prev_rank = int(prev_value)
                            if prev_rank < opening_rank:
                                opening_rank = prev_rank
                        except ValueError:
                            pass
                
                branch = cutoff.unique_key
                recommendations.append({
                    'unique_key': branch.unique_key,
                    'college': {
                        'college_id': branch.college.college_id,
                        'college_code': branch.college.college_code,
                        'college_name': branch.college.college_name,
                        'location': branch.college.location,
                    },
                    'branch': {
                        'branch_id': branch.branch_id,
                        'branch_name': branch.branch_name,
                    },
                    'cluster': {
                        'cluster_code': branch.cluster.cluster_code,
                        'cluster_name': branch.cluster.cluster_name,
                    },
                    'category': cutoff.category,
                    'opening_rank': opening_rank,
                    'closing_rank': closing_rank,
                    'distance_from_rank': distance,
                    'eligibility_flag': True,
                })
        except ValueError:
            # If cutoff value is not a number, skip
            continue
    
    # Sort by distance_from_rank (closest first)
    recommendations.sort(key=lambda x: x['distance_from_rank'])
    
    return recommendations

