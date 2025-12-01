from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from students.models import Student
from .models import CounsellingChoice
from .serializers import CounsellingChoiceSerializer, CounsellingChoiceCreateSerializer
from .utils import get_recommendations


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    """
    Get rank-based recommendations for counselling students.
    Body: { kcet_rank, category?, year?, round? }
    """
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can access recommendations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    kcet_rank = request.data.get('kcet_rank')
    if not kcet_rank:
        # Use student's saved rank
        kcet_rank = student.kcet_rank
    
    if not kcet_rank:
        return Response(
            {'error': 'kcet_rank is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    category = request.data.get('category')
    year = request.data.get('year', '2025')
    round_name = request.data.get('round', 'r1')
    
    recommendations_list = get_recommendations(kcet_rank, category, year, round_name)
    
    return Response({
        'kcet_rank': kcet_rank,
        'category': category,
        'year': year,
        'round': round_name,
        'recommendations': recommendations_list,
        'count': len(recommendations_list),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def choices_list(request):
    """Get all counselling choices for the logged-in student"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can access choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    choices = CounsellingChoice.objects.filter(
        student_user_id=student
    ).order_by('order_of_list').select_related('unique_key__college', 'unique_key__cluster')
    
    serializer = CounsellingChoiceSerializer(choices, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def choices_create(request):
    """Add a new counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can create choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CounsellingChoiceCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if unique_key already exists for this student
        unique_key = serializer.validated_data['unique_key']
        order_of_list = serializer.validated_data['order_of_list']
        
        existing = CounsellingChoice.objects.filter(
            student_user_id=student,
            unique_key=unique_key
        ).first()
        
        if existing:
            return Response(
                {'error': 'This branch is already in your choices'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        existing_order = CounsellingChoice.objects.filter(
            student_user_id=student,
            order_of_list=order_of_list
        ).first()
        
        if existing_order:
            return Response(
                {'error': f'Order {order_of_list} is already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        choice = CounsellingChoice.objects.create(
            student_user_id=student,
            **serializer.validated_data
        )
        
        return Response(
            CounsellingChoiceSerializer(choice).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def choices_update(request, choice_id):
    """Update order_of_list for a counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can update choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        choice = CounsellingChoice.objects.get(choice_id=choice_id, student_user_id=student)
    except CounsellingChoice.DoesNotExist:
        return Response(
            {'error': 'Choice not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_order = request.data.get('order_of_list')
    if new_order is None:
        return Response(
            {'error': 'order_of_list is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if new order is already taken
    existing = CounsellingChoice.objects.filter(
        student_user_id=student,
        order_of_list=new_order
    ).exclude(choice_id=choice_id).first()
    
    if existing:
        return Response(
            {'error': f'Order {new_order} is already taken'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    choice.order_of_list = new_order
    choice.save()
    
    return Response(CounsellingChoiceSerializer(choice).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def choices_delete(request, choice_id):
    """Delete a counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can delete choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        choice = CounsellingChoice.objects.get(choice_id=choice_id, student_user_id=student)
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CounsellingChoice.DoesNotExist:
        return Response(
            {'error': 'Choice not found'},
            status=status.HTTP_404_NOT_FOUND
        )

