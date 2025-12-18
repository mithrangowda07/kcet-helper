from colleges.models import Branch, Cutoff, Category
from django.db.models import Q


def get_recommendations(kcet_rank, category=None, year='2025', opening_rank=None, closing_rank=None, cluster=None):
    """
    Get recommended branches based on KCET rank with opening and closing rank filters.
    
    Args:
        kcet_rank: Student's KCET rank
        category: Category (e.g., 'GM', 'SC', 'ST', etc.)
        year: Year to check (default '2025')
        opening_rank: Minimum opening rank (Round 1 cutoff) - filters branches where cutoff_round1 >= opening_rank
        closing_rank: Maximum closing rank (Round 3 cutoff) - filters branches where cutoff_round3 <= closing_rank
        cluster: Cluster code to filter by (optional)
    
    Returns:
        List of recommended branches with cutoff information
    """
    cutoff_field_r1 = f'cutoff_{year}_r1'
    cutoff_field_r3 = f'cutoff_{year}_r3'
    
    # Get all cutoffs for the specified year
    cutoffs = Cutoff.objects.select_related('unique_key__college', 'unique_key__cluster').all()
    
    # Filter by cluster if provided
    if cluster:
        cutoffs = cutoffs.filter(unique_key__cluster__cluster_code=cluster)
    
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
        
        # Get Round 1 and Round 3 cutoff values
        cutoff_r1_value = getattr(cutoff, cutoff_field_r1, None)
        cutoff_r3_value = getattr(cutoff, cutoff_field_r3, None)
        
        # Skip if either cutoff is missing
        if not cutoff_r1_value or cutoff_r1_value == '' or not cutoff_r3_value or cutoff_r3_value == '':
            continue
        
        try:
            # Parse as integers
            cutoff_r1 = int(cutoff_r1_value)
            cutoff_r3 = int(cutoff_r3_value)
            
            # Apply filters: cutoff_round1 >= openingRank AND cutoff_round3 <= closingRank
            if opening_rank is not None and cutoff_r1 < opening_rank:
                continue
            if closing_rank is not None and cutoff_r3 > closing_rank:
                continue
            
            # Calculate distance (closing rank - opening rank)
            distance = cutoff_r3 - cutoff_r1
            
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
                'opening_rank': cutoff_r1,  # Round 1 cutoff
                'closing_rank': cutoff_r3,   # Round 3 cutoff
                'distance_from_rank': distance,
                'eligibility_flag': True,
            })
        except ValueError:
            # If cutoff value is not a number, skip
            continue
    
    # Sort by distance_from_rank (closest first)
    recommendations.sort(key=lambda x: x['distance_from_rank'])
    
    return recommendations

