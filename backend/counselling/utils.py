"""
Advanced KCET Recommendation Engine

This module implements a sophisticated recommendation algorithm with:
1. Round-based cutoff selection with fallback
2. Dynamic opening & closing rank calculation
3. Multi-year cutoff stabilization
4. Duplicate removal
5. Cluster-based filtering
6. Advanced sorting
"""

from colleges.models import Branch, Cutoff, Category
from django.db.models import Q, F, Case, When, Value, IntegerField, Min, Max
from django.db.models.functions import Coalesce
from typing import List, Dict, Optional, Tuple
import statistics


def get_round_fallback_order(selected_round: str) -> List[str]:
    """
    Get fallback order for round selection.
    
    Fallback order:
    - R1 → R2 → R3
    - R2 → R1 → R3
    - R3 → R2 → R1
    
    Args:
        selected_round: Selected round (R1, R2, or R3)
    
    Returns:
        List of rounds in fallback order
    """
    selected_round = selected_round.upper()
    
    # Default fallback orders
    fallback_orders = {
        'R1': ['R1', 'R2', 'R3'],
        'R2': ['R2', 'R1', 'R3'],
        'R3': ['R3', 'R2', 'R1'],
    }
    
    return fallback_orders.get(selected_round, ['R1', 'R2', 'R3'])


def resolve_cutoff_with_fallback(
    branch: Branch,
    category: str,
    year: str,
    selected_round: str,
    fallback_order: List[str]
) -> Optional[int]:
    """
    Resolve cutoff for a branch using round fallback logic.
    Returns the first available cutoff value from fallback order.
    
    Args:
        branch: Branch object
        category: Category string
        year: Year string (e.g., '2025')
        selected_round: Selected round (R1, R2, R3)
        fallback_order: List of rounds in fallback order
    
    Returns:
        Cutoff value as integer, or None if not found
    """
    for round_name in fallback_order:
        cutoff_field = f'cutoff_{year}_{round_name.lower()}'
        try:
            cutoff_obj = Cutoff.objects.get(unique_key=branch, category=category)
            value = getattr(cutoff_obj, cutoff_field, None)
            
            if value and value not in [None, '', 'NA', '-', 'nan']:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    continue
        except Cutoff.DoesNotExist:
            continue
    
    return None


def calculate_rank_band(user_rank: int) -> str:
    """
    Determine rank band based on user rank.
    
    Args:
        user_rank: User's KCET rank
    
    Returns:
        Rank band: 'tight', 'medium', 'wide', or 'very_wide'
    """
    if user_rank <= 1000:
        return 'tight'
    elif user_rank <= 5000:
        return 'medium'
    elif user_rank <= 20000:
        return 'wide'
    else:
        return 'very_wide'


def calculate_rank_window(user_rank: int) -> Tuple[int, int]:
    """
    Calculate dynamic opening and closing rank based on user rank.
    
    Args:
        user_rank: User's KCET rank
    
    Returns:
        Tuple of (opening_rank, closing_rank)
    """
    band = calculate_rank_band(user_rank)
    
    if band == 'tight':
        opening_rank = int(user_rank * 0.4)
        closing_rank = int(user_rank * 2.5)
    elif band == 'medium':
        opening_rank = int(user_rank * 0.6)
        closing_rank = int(user_rank * 3)
    elif band == 'wide':
        opening_rank = int(user_rank * 0.7)
        closing_rank = int(user_rank * 3.5)
    else:  # very_wide
        opening_rank = int(user_rank * 0.8)
        closing_rank = int(user_rank * 4)
    
    return opening_rank, closing_rank


def get_multi_year_cutoffs(branch: Branch, category: str, years: List[str], round_name: str) -> List[int]:
    """
    Get cutoff values for multiple years for a branch.
    
    Args:
        branch: Branch object
        category: Category string
        years: List of years to check (e.g., ['2022', '2023', '2024', '2025'])
        round_name: Round name (r1, r2, r3)
    
    Returns:
        List of cutoff values (integers) for available years
    """
    cutoffs = []
    try:
        cutoff_obj = Cutoff.objects.get(unique_key=branch, category=category)
        for year in years:
            cutoff_field = f'cutoff_{year}_{round_name}'
            value = getattr(cutoff_obj, cutoff_field, None)
            if value and value not in [None, '', 'NA', '-', 'nan']:
                try:
                    cutoffs.append(int(value))
                except (ValueError, TypeError):
                    continue
    except Cutoff.DoesNotExist:
        pass
    
    return cutoffs


def stabilize_cutoff(cutoffs: List[int]) -> Optional[int]:
    """
    Stabilize cutoff using multi-year data.
    Prefer latest year, use median if high fluctuation, ignore spikes.
    
    Args:
        cutoffs: List of cutoff values from multiple years
    
    Returns:
        Stabilized cutoff value, or None if no valid data
    """
    if not cutoffs:
        return None
    
    if len(cutoffs) == 1:
        return cutoffs[0]
    
    # Sort to get latest (assuming years are in order)
    sorted_cutoffs = sorted(cutoffs)
    
    # Calculate coefficient of variation (CV) to detect fluctuation
    if len(sorted_cutoffs) >= 2:
        mean = statistics.mean(sorted_cutoffs)
        if mean > 0:
            std_dev = statistics.stdev(sorted_cutoffs) if len(sorted_cutoffs) > 1 else 0
            cv = std_dev / mean
            
            # If high fluctuation (CV > 0.15), use median
            if cv > 0.15:
                return int(statistics.median(sorted_cutoffs))
    
    # Prefer latest (highest value, assuming later years have higher cutoffs)
    # Actually, we want the most recent, so if cutoffs are from 2022-2025,
    # the last in the list should be latest
    return sorted_cutoffs[-1]


def check_historical_relaxation(
    branch: Branch,
    category: str,
    user_rank: int,
    years: List[str],
    round_name: str
) -> bool:
    """
    Check if branch should be included based on historical relaxation rule.
    
    Include if:
    - Any year cutoff <= user_rank * 0.8
    OR
    - Latest year cutoff > user_rank BUT:
        - Past year cutoff was lower
        - OR cutoff dropped >= 15% in any year
    
    Args:
        branch: Branch object
        category: Category string
        user_rank: User's KCET rank
        years: List of years to check
        round_name: Round name (r1, r2, r3)
    
    Returns:
        True if branch should be included, False otherwise
    """
    cutoffs = get_multi_year_cutoffs(branch, category, years, round_name)
    
    if not cutoffs:
        return False
    
    # Check if any year cutoff <= user_rank * 0.8
    threshold = int(user_rank * 0.8)
    if any(c <= threshold for c in cutoffs):
        return True
    
    # Check latest year cutoff
    latest_cutoff = cutoffs[-1] if cutoffs else None
    
    if latest_cutoff and latest_cutoff > user_rank:
        # Check if past year cutoff was lower (meaning cutoff increased, making it harder)
        # This means there was a year where cutoff was lower, so it might drop again
        if len(cutoffs) >= 2:
            past_cutoff = cutoffs[-2]
            # If past cutoff was lower than latest, it means cutoff increased
            # But we want to include if there was any year with lower cutoff
            if any(c < latest_cutoff for c in cutoffs[:-1]):
                return True
        
        # Check if cutoff dropped >= 15% in any year
        for i in range(1, len(cutoffs)):
            prev_cutoff = cutoffs[i-1]
            curr_cutoff = cutoffs[i]
            if prev_cutoff > 0:
                drop_percentage = ((prev_cutoff - curr_cutoff) / prev_cutoff) * 100
                if drop_percentage >= 15:
                    return True
    
    return False


def get_recommendations(
    kcet_rank: int,
    category: Optional[str] = None,
    year: str = '2025',
    round_name: str = 'R1',
    cluster: Optional[str] = None,
    opening_rank: Optional[int] = None,
    closing_rank: Optional[int] = None
) -> List[Dict]:
    """
    Advanced recommendation engine with dynamic rank calculation and multi-year analysis.
    
    Args:
        kcet_rank: Student's KCET rank
        category: Category (e.g., 'GM', '1R', etc.) - uses student's category if None
        year: Year to check (default '2025')
        round_name: Selected round (R1, R2, R3) - default 'R1'
        cluster: Cluster code to filter by (optional)
        opening_rank: User-specified opening rank (if None, calculated dynamically)
        closing_rank: User-specified closing rank (if None, calculated dynamically)
    
    Returns:
        List of recommended branches with cutoff information
    """
    # Calculate dynamic opening and closing ranks if not provided
    if opening_rank is None or closing_rank is None:
        calculated_opening, calculated_closing = calculate_rank_window(kcet_rank)
        if opening_rank is None:
            opening_rank = calculated_opening
        if closing_rank is None:
            closing_rank = calculated_closing
    
    # Normalize round name
    round_name = round_name.upper()
    round_lower = round_name.lower()
    
    # Get round fallback order (independent of category)
    fallback_order = get_round_fallback_order(round_name)
    
    # Years for multi-year analysis
    years = ['2022', '2023', '2024', '2025']
    
    # Get all branches with cutoffs
    branches_qs = Branch.objects.select_related('college', 'cluster').all()
    
    # Filter by cluster if provided
    if cluster:
        branches_qs = branches_qs.filter(cluster__cluster_code=cluster)
    
    # Get valid categories for filtering
    valid_categories = set()
    if category:
        try:
            cat_obj = Category.objects.get(category=category)
            fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',') if c.strip()]
            valid_categories = set(fall_back_list)
        except Category.DoesNotExist:
            valid_categories = {category}
    else:
        # If no category provided, get all categories
        valid_categories = set(Category.objects.values_list('category', flat=True))
    
    recommendations_dict = {}  # Use dict to remove duplicates: key = (college_id, branch_id)
    
    # Process each branch
    for branch in branches_qs:
        # Try each valid category
        best_cutoff = None
        best_category = None
        
        for cat in valid_categories:
            # Resolve cutoff with fallback
            cutoff_value = resolve_cutoff_with_fallback(
                branch, cat, year, round_name, fallback_order
            )
            
            if cutoff_value is not None:
                # Get multi-year cutoffs for stabilization
                multi_year_cutoffs = get_multi_year_cutoffs(branch, cat, years, round_lower)
                
                if multi_year_cutoffs:
                    # Stabilize cutoff
                    stabilized_cutoff = stabilize_cutoff(multi_year_cutoffs)
                    
                    if stabilized_cutoff is not None:
                        # Use stabilized cutoff if available, otherwise use resolved cutoff
                        final_cutoff = stabilized_cutoff
                    else:
                        final_cutoff = cutoff_value
                else:
                    final_cutoff = cutoff_value
                
                # STRICT FILTERING: Only include if cutoff is within range
                # cutoff >= opening_rank AND cutoff <= closing_rank
                if opening_rank <= final_cutoff <= closing_rank:
                    if best_cutoff is None or final_cutoff < best_cutoff:
                        best_cutoff = final_cutoff
                        best_category = cat
        
        # If we found a valid cutoff, add to recommendations
        if best_cutoff is not None:
            # Use (college_id, branch_id) as key to remove duplicates
            key = (branch.college.college_id, branch.branch_id)
            
            if key not in recommendations_dict:
                recommendations_dict[key] = {
                    'unique_key': branch.unique_key,
                    'public_id': str(branch.public_id),
                    'college': {
                        'public_id': str(branch.college.public_id),
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
                    'category': best_category,
                    'cutoff': best_cutoff,
                    'distance_from_rank': abs(best_cutoff - kcet_rank),
                    'eligibility_flag': best_cutoff <= kcet_rank,
                }
            else:
                # If duplicate exists, keep the one with better (closer) cutoff
                existing = recommendations_dict[key]
                if abs(best_cutoff - kcet_rank) < existing['distance_from_rank']:
                    existing['cutoff'] = best_cutoff
                    existing['distance_from_rank'] = abs(best_cutoff - kcet_rank)
                    existing['eligibility_flag'] = best_cutoff <= kcet_rank
                    existing['category'] = best_category
    
    # Convert to list
    recommendations = list(recommendations_dict.values())
    
    # Sort by cutoff in ascending order (lowest cutoff first)
    recommendations.sort(key=lambda x: x['cutoff'])
    
    return recommendations
