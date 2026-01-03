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

