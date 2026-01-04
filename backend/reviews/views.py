from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg
from django.core.cache import cache
from .models import CollegeReview
from .serializers import CollegeReviewSerializer, CollegeReviewCreateSerializer
from colleges.models import Branch
from .review_checker import check_review, is_model_loaded
import logging

logger = logging.getLogger(__name__)

# Review text fields mapping (field_name -> display_name)
REVIEW_FIELDS = {
    'teaching_review': 'Teaching Quality',
    'courses_review': 'Course Curriculum',
    'library_review': 'Library Facilities',
    'research_review': 'Research Opportunities',
    'internship_review': 'Internship Support',
    'infrastructure_review': 'Infrastructure',
    'administration_review': 'Administration',
    'extracurricular_review': 'Extracurricular Activities',
    'safety_review': 'Safety & Security',
    'placement_review': 'Placement Support',
}


def validate_review_texts(review_data):
    """
    Validate all review text fields using ML model.
    
    Args:
        review_data: Dictionary containing review fields
        
    Returns:
        dict: {
            'results': {field_name: 'HUMAN-WRITTEN'|'AI-GENERATED', ...},
            'can_submit': bool,
            'ai_fields': [field_name, ...]  # Fields detected as AI
        }
    """
    if not is_model_loaded():
        logger.error("ML model not loaded, cannot validate reviews")
        # If model not loaded, fail closed - don't allow submission
        return {
            'results': {},
            'can_submit': False,
            'ai_fields': [],
            'error': 'AI detection model not available'
        }
    
    results = {}
    ai_fields = []
    
    # Check each review text field
    for field_name, display_name in REVIEW_FIELDS.items():
        text = review_data.get(field_name, '').strip()
        
        if not text:
            # Empty text is considered valid (human)
            results[field_name] = 'HUMAN-WRITTEN'
            continue
        
        try:
            label, probability_ai = check_review(text)
            results[field_name] = label
            
            if label == 'AI-GENERATED':
                ai_fields.append(field_name)
                logger.warning(f"AI-generated text detected in {field_name} (probability: {probability_ai:.3f})")
        except Exception as e:
            logger.error(f"Error validating {field_name}: {str(e)}", exc_info=True)
            # On error, fail closed - don't allow submission
            results[field_name] = 'AI-GENERATED'
            ai_fields.append(field_name)
    
    return {
        'results': results,
        'can_submit': len(ai_fields) == 0,
        'ai_fields': ai_fields
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_text(request):
    """
    Check if a single text field is AI-generated or Human-written.
    
    POST /api/review/check-text/
    {
        "field": "teaching_quality",
        "text": "The teaching quality at RVCE is strong..."
    }
    
    Response:
    {
        "field": "teaching_quality",
        "label": "HUMAN-WRITTEN",  // or "AI-GENERATED"
        "ai_probability": 0.23
    }
    """
    if not is_model_loaded():
        return Response(
            {'error': 'AI detection model not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    field = request.data.get('field', '').strip()
    text = request.data.get('text', '').strip()
    
    if not field:
        return Response(
            {'error': 'Field name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate field name - accept both field names with/without _review suffix
    field_base = field.replace('_review', '')
    if field not in REVIEW_FIELDS and f"{field_base}_review" not in REVIEW_FIELDS:
        return Response(
            {'error': f'Invalid field name: {field}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Rate limiting: 10 requests per minute per user
    user_id = str(request.user.student_user_id)
    cache_key = f'text_check_rate_limit_{user_id}'
    request_count = cache.get(cache_key, 0)
    
    if request_count >= 10:
        return Response(
            {'error': 'Rate limit exceeded. Please wait before checking again.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    cache.set(cache_key, request_count + 1, 60)  # 60 seconds
    
    try:
        label, probability_ai = check_review(text)
        
        return Response({
            'field': field,
            'label': label,
            'ai_probability': round(probability_ai, 3)
        })
    except Exception as e:
        logger.error(f"Error checking text: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Error processing text. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_all(request):
    """
    Validate all review text fields in batch.
    
    POST /api/review/validate-all/
    {
        "reviews": {
            "teaching_quality": "...",
            "course_curriculum": "...",
            "library": "...",
            "research": "..."
        }
    }
    
    Response:
    {
        "results": {
            "teaching_quality": "HUMAN-WRITTEN",
            "course_curriculum": "HUMAN-WRITTEN",
            "library": "AI-GENERATED",
            "research": "HUMAN-WRITTEN"
        },
        "can_submit": false
    }
    """
    if not is_model_loaded():
        return Response(
            {'error': 'AI detection model not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    reviews_data = request.data.get('reviews', {})
    
    if not isinstance(reviews_data, dict):
        return Response(
            {'error': 'reviews must be a dictionary'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Normalize field names - accept both with/without _review suffix
    normalized_reviews = {}
    for key, value in reviews_data.items():
        # If key doesn't end with _review, try to find matching field
        if key.endswith('_review'):
            normalized_reviews[key] = value
        else:
            # Try to find matching field with _review suffix
            matching_field = None
            for field_name in REVIEW_FIELDS.keys():
                if field_name.replace('_review', '') == key:
                    matching_field = field_name
                    break
            if matching_field:
                normalized_reviews[matching_field] = value
            else:
                # Use as-is if no match found
                normalized_reviews[key] = value
    
    # Validate all review texts
    validation_result = validate_review_texts(normalized_reviews)
    
    return Response(validation_result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_create(request):
    """Create or update a review (only for studying students) - one review per branch per user"""
    student = request.user

    if student.type_of_student != 'studying':
        return Response(
            {'error': 'Only studying students can create reviews'},
            status=status.HTTP_403_FORBIDDEN
        )

    # The student's profile must already have a branch assigned.
    branch = getattr(student, 'unique_key', None)
    if branch is None:
        return Response(
            {'error': 'Your profile is missing a branch. Please contact support.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CollegeReviewCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # CRITICAL: Validate all review texts using ML model before saving
    # This prevents AI-generated reviews even if frontend is bypassed
    validation_result = validate_review_texts(serializer.validated_data)
    
    if not validation_result['can_submit']:
        # Build user-friendly error message
        ai_field_names = [
            REVIEW_FIELDS.get(field, field.replace('_review', '').replace('_', ' ').title())
            for field in validation_result['ai_fields']
        ]
        
        return Response(
            {
                'error': 'Review submission rejected: AI-generated content detected',
                'message': f'The following review fields contain AI-generated text: {", ".join(ai_field_names)}',
                'ai_fields': validation_result['ai_fields'],
                'field_display_names': ai_field_names,
                'validation_results': validation_result['results']
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prevent users from spoofing another branch; always use the profile branch.
    payload_unique_key = serializer.validated_data.get('unique_key')
    if payload_unique_key and payload_unique_key != branch:
        return Response(
            {'error': 'You can only review your own branch.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if student already reviewed this branch
    existing = CollegeReview.objects.filter(
        student_user_id=student,
        unique_key=branch
    ).first()

    if existing:
        # Update existing review
        for key, value in serializer.validated_data.items():
            if key != 'unique_key':  # Don't update unique_key
                setattr(existing, key, value)
        existing.save()

        return Response(
            CollegeReviewSerializer(existing).data,
            status=status.HTTP_200_OK
        )

    # Create new review
    review = CollegeReview.objects.create(
        student_user_id=student,
        unique_key=branch,
        **{k: v for k, v in serializer.validated_data.items() if k != 'unique_key'}
    )

    return Response(
        CollegeReviewSerializer(review).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_review(request, unique_key):
    """Get current user's review for a specific branch"""
    student = request.user

    if student.type_of_student != 'studying':
        return Response(
            {'error': 'Only studying students can access reviews'},
            status=status.HTTP_403_FORBIDDEN
        )

    branch = getattr(student, 'unique_key', None)
    if branch is None:
        return Response(
            {'error': 'Your profile is missing a branch. Please contact support.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Keep the path parameter for backward compatibility but enforce profile branch.
    if unique_key and unique_key != branch.unique_key:
        return Response(
            {
                'error': 'You can only access the review for your assigned branch.',
                'branch': branch.unique_key,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        review = CollegeReview.objects.get(
            student_user_id=student,
            unique_key=branch
        )
        serializer = CollegeReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CollegeReview.DoesNotExist:
        return Response({'review': None}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_my_review(request, unique_key):
    """Delete the current student's review for their branch"""
    student = request.user

    if student.type_of_student != 'studying':
        return Response(
            {'error': 'Only studying students can delete reviews'},
            status=status.HTTP_403_FORBIDDEN
        )

    branch = getattr(student, 'unique_key', None)
    if branch is None:
        return Response(
            {'error': 'Your profile is missing a branch. Please contact support.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if unique_key and unique_key != branch.unique_key:
        return Response(
            {
                'error': 'You can only delete the review for your assigned branch.',
                'branch': branch.unique_key,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        review = CollegeReview.objects.get(
            student_user_id=student,
            unique_key=branch
        )
    except CollegeReview.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def branch_reviews(request, public_id):
    """Get all reviews for a specific branch"""
    try:
        branch = Branch.objects.get(public_id=public_id)
    except Branch.DoesNotExist:
        return Response(
            {'error': 'Branch not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    reviews = CollegeReview.objects.filter(
        unique_key=branch
    ).select_related('student_user_id', 'unique_key__college', 'unique_key__cluster')
    
    serializer = CollegeReviewSerializer(reviews, many=True)
    
    # Calculate average ratings
    avg_ratings = reviews.aggregate(
        avg_teaching=Avg('teaching_rating'),
        avg_courses=Avg('courses_rating'),
        avg_library=Avg('library_rating'),
        avg_research=Avg('research_rating'),
        avg_internship=Avg('internship_rating'),
        avg_infrastructure=Avg('infrastructure_rating'),
        avg_administration=Avg('administration_rating'),
        avg_extracurricular=Avg('extracurricular_rating'),
        avg_safety=Avg('safety_rating'),
        avg_placement=Avg('placement_rating'),
    )
    
    return Response({
        'reviews': serializer.data,
        'average_ratings': avg_ratings,
        'total_reviews': reviews.count(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def college_reviews(request, public_id):
    """Get aggregated reviews for all branches in a college"""
    from colleges.models import College
    
    try:
        college = College.objects.get(public_id=public_id)
    except College.DoesNotExist:
        return Response(
            {'error': 'College not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    branches = Branch.objects.filter(college=college)
    reviews = CollegeReview.objects.filter(
        unique_key__in=branches
    ).select_related('student_user_id', 'unique_key')
    
    # Aggregate by branch
    branch_reviews = {}
    for branch in branches:
        branch_review_list = reviews.filter(unique_key=branch)
        if branch_review_list.exists():
            avg_ratings = branch_review_list.aggregate(
                avg_teaching=Avg('teaching_rating'),
                avg_courses=Avg('courses_rating'),
                avg_library=Avg('library_rating'),
                avg_research=Avg('research_rating'),
                avg_internship=Avg('internship_rating'),
                avg_infrastructure=Avg('infrastructure_rating'),
                avg_administration=Avg('administration_rating'),
                avg_extracurricular=Avg('extracurricular_rating'),
                avg_safety=Avg('safety_rating'),
                avg_placement=Avg('placement_rating'),
            )
            branch_reviews[branch.unique_key] = {
                'branch_name': branch.branch_name,
                'average_ratings': avg_ratings,
                'total_reviews': branch_review_list.count(),
            }
    
    # Overall college averages
    overall_avg = reviews.aggregate(
        avg_teaching=Avg('teaching_rating'),
        avg_courses=Avg('courses_rating'),
        avg_library=Avg('library_rating'),
        avg_research=Avg('research_rating'),
        avg_internship=Avg('internship_rating'),
        avg_infrastructure=Avg('infrastructure_rating'),
        avg_administration=Avg('administration_rating'),
        avg_extracurricular=Avg('extracurricular_rating'),
        avg_safety=Avg('safety_rating'),
        avg_placement=Avg('placement_rating'),
    )
    
    return Response({
        'college_id': str(college.public_id),
        'college_name': college.college_name,
        'branch_reviews': branch_reviews,
        'overall_average_ratings': overall_avg,
        'total_reviews': reviews.count(),
    })

