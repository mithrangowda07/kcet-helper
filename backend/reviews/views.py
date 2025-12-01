from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg
from .models import CollegeReview
from .serializers import CollegeReviewSerializer, CollegeReviewCreateSerializer
from colleges.models import Branch


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_create(request):
    """Create a review (only for studying students)"""
    student = request.user
    
    if student.type_of_student != 'studying':
        return Response(
            {'error': 'Only studying students can create reviews'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CollegeReviewCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if student already reviewed this branch
        unique_key = serializer.validated_data['unique_key']
        existing = CollegeReview.objects.filter(
            student_user_id=student,
            unique_key=unique_key
        ).first()
        
        if existing:
            return Response(
                {'error': 'You have already reviewed this branch'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review = CollegeReview.objects.create(
            student_user_id=student,
            **serializer.validated_data
        )
        
        return Response(
            CollegeReviewSerializer(review).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def branch_reviews(request, unique_key):
    """Get all reviews for a specific branch"""
    try:
        branch = Branch.objects.get(unique_key=unique_key)
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
def college_reviews(request, college_id):
    """Get aggregated reviews for all branches in a college"""
    from colleges.models import College
    
    try:
        college = College.objects.get(college_id=college_id)
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
        'college_id': college_id,
        'college_name': college.college_name,
        'branch_reviews': branch_reviews,
        'overall_average_ratings': overall_avg,
        'total_reviews': reviews.count(),
    })

