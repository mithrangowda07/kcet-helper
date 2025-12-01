from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import StudentMeeting
from .serializers import (
    StudentMeetingSerializer, StudentMeetingRequestSerializer,
    StudentMeetingStatusUpdateSerializer
)
from .services import create_google_meet_event
from students.models import Student


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_request(request):
    """Counselling student requests a meeting with a studying student"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can request meetings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = StudentMeetingRequestSerializer(data=request.data)
    if serializer.is_valid():
        studying_user_id = serializer.validated_data['studying_user_id']
        scheduled_time = serializer.validated_data.get('scheduled_time')
        
        # Verify studying_user_id is a studying student
        try:
            studying_student = Student.objects.get(
                student_user_id=studying_user_id,
                type_of_student='studying',
                is_active=True
            )
        except Student.DoesNotExist:
            return Response(
                {'error': 'Studying student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if meeting already exists
        existing = StudentMeeting.objects.filter(
            counselling_user_id=student,
            studying_user_id=studying_student,
            status__in=['requested', 'accepted']
        ).first()
        
        if existing:
            return Response(
                {'error': 'A meeting request already exists with this student'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meeting = StudentMeeting.objects.create(
            counselling_user_id=student,
            studying_user_id=studying_student,
            scheduled_time=scheduled_time,
            status='requested'
        )
        
        return Response(
            StudentMeetingSerializer(meeting).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_requests(request):
    """Get all meeting requests made by counselling student"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    meetings = StudentMeeting.objects.filter(
        counselling_user_id=student
    ).select_related('studying_user_id', 'counselling_user_id').order_by('-created_at')
    
    serializer = StudentMeetingSerializer(meetings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_invitations(request):
    """Get all meeting invitations for studying student"""
    student = request.user
    
    if student.type_of_student != 'studying':
        return Response(
            {'error': 'Only studying students can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    meetings = StudentMeeting.objects.filter(
        studying_user_id=student
    ).select_related('counselling_user_id', 'studying_user_id').order_by('-created_at')
    
    serializer = StudentMeetingSerializer(meetings, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def meeting_status_update(request, meeting_id):
    """Update meeting status (accept/reject/cancel/complete)"""
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.select_related(
            'counselling_user_id', 'studying_user_id'
        ).get(meeting_id=meeting_id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = StudentMeetingStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    new_status = serializer.validated_data['status']
    
    # Check permissions
    if new_status == 'accepted':
        # Only studying student can accept
        if student != meeting.studying_user_id:
            return Response(
                {'error': 'Only the studying student can accept meetings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if meeting.status != 'requested':
            return Response(
                {'error': 'Only requested meetings can be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get scheduled_time from request or use default (1 day from now)
        scheduled_time = serializer.validated_data.get('scheduled_time')
        if not scheduled_time:
            scheduled_time = timezone.now() + timedelta(days=1)
        
        # Create Google Calendar event
        result = create_google_meet_event(
            counselling_email=meeting.counselling_user_id.email_id,
            studying_email=meeting.studying_user_id.email_id,
            scheduled_time=scheduled_time,
            duration_minutes=meeting.duration_minutes
        )
        
        if result:
            meeting.scheduled_time = result['scheduled_time']
            meeting.meet_link = result['meet_link']
            meeting.status = 'accepted'
            meeting.save()
            
            # TODO: Send email notifications to both students
            
            return Response(StudentMeetingSerializer(meeting).data)
        else:
            return Response(
                {'error': 'Failed to create Google Calendar event. Please check server configuration.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif new_status == 'rejected':
        # Only studying student can reject
        if student != meeting.studying_user_id:
            return Response(
                {'error': 'Only the studying student can reject meetings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        meeting.status = 'rejected'
        meeting.save()
        return Response(StudentMeetingSerializer(meeting).data)
    
    elif new_status in ['completed', 'cancelled']:
        # Either party can mark as completed or cancelled
        if student not in [meeting.counselling_user_id, meeting.studying_user_id]:
            return Response(
                {'error': 'You are not authorized to update this meeting'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        meeting.status = new_status
        meeting.save()
        return Response(StudentMeetingSerializer(meeting).data)
    
    return Response(
        {'error': 'Invalid status'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def branch_students(request, unique_key):
    """Get list of studying students for a branch (for counselling students to request meetings)"""
    from colleges.models import Branch
    
    try:
        branch = Branch.objects.get(unique_key=unique_key)
    except Branch.DoesNotExist:
        return Response(
            {'error': 'Branch not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get studying students from this branch who have created reviews
    from reviews.models import CollegeReview
    
    students_with_reviews = Student.objects.filter(
        type_of_student='studying',
        unique_key=branch,
        is_active=True
    ).filter(
        college_reviews__unique_key=branch
    ).distinct()
    
    # Return basic info (no sensitive data)
    students_data = []
    for student in students_with_reviews:
        students_data.append({
            'student_user_id': student.student_user_id,
            'year_of_starting': student.year_of_starting,
            'has_review': True,
        })
    
    return Response({
        'branch': {
            'unique_key': branch.unique_key,
            'branch_name': branch.branch_name,
            'college_name': branch.college.college_name,
        },
        'students': students_data,
        'count': len(students_data),
    })

