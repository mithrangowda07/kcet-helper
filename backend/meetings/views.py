from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime
from .models import StudentMeeting
from .serializers import StudentMeetingSerializer, MeetingRequestSerializer
from .services import generate_jitsi_meeting_link
from students.models import Student


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_request(request):
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can request meetings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = MeetingRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    studying_user_id = serializer.validated_data['studying_user_id']
    
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
    
    meeting = StudentMeeting.objects.create(
        counselling_user_id=student,
        studying_user_id=studying_student,
        status='requested'
    )
    
    return Response(
        StudentMeetingSerializer(meeting).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_accept(request, id):
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.get(meeting_id=id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
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
    
    scheduled_time = request.data.get('scheduled_time')
    if scheduled_time:
        try:
            if isinstance(scheduled_time, str):
                scheduled_time = scheduled_time.replace('Z', '+00:00')
                scheduled_time = datetime.fromisoformat(scheduled_time)
            if timezone.is_naive(scheduled_time):
                scheduled_time = timezone.make_aware(scheduled_time)
        except Exception:
            scheduled_time = timezone.now() + timedelta(days=1)
    else:
        scheduled_time = timezone.now() + timedelta(days=1)
    
    meet_link = generate_jitsi_meeting_link(
        meeting.studying_user_id.student_user_id,
        meeting.counselling_user_id.student_user_id
    )
    
    meeting.scheduled_time = scheduled_time
    meeting.duration_minutes = request.data.get('duration_minutes', 30)
    meeting.meet_link = meet_link
    meeting.status = 'accepted'
    meeting.save()
    
    return Response(StudentMeetingSerializer(meeting).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_reject(request, id):
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.get(meeting_id=id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if student != meeting.studying_user_id:
        return Response(
            {'error': 'Only the studying student can reject meetings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    meeting.status = 'rejected'
    meeting.save()
    
    return Response(StudentMeetingSerializer(meeting).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_cancel(request, id):
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.get(meeting_id=id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if student not in [meeting.counselling_user_id, meeting.studying_user_id]:
        return Response(
            {'error': 'You are not authorized to cancel this meeting'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if meeting.status not in ['requested', 'accepted']:
        return Response(
            {'error': 'Only requested or accepted meetings can be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    meeting.status = 'cancelled'
    meeting.save()
    
    return Response(StudentMeetingSerializer(meeting).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_complete(request, id):
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.get(meeting_id=id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if student not in [meeting.counselling_user_id, meeting.studying_user_id]:
        return Response(
            {'error': 'You are not authorized to complete this meeting'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    meeting.status = 'completed'
    meeting.save()
    
    return Response(StudentMeetingSerializer(meeting).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meetings_upcoming(request):
    student = request.user
    
    meetings = StudentMeeting.objects.filter(
        status__in=['requested', 'accepted']
    ).filter(
        Q(counselling_user_id=student) | Q(studying_user_id=student)
    ).select_related('counselling_user_id', 'studying_user_id').order_by('scheduled_time', 'created_at')
    
    serializer = StudentMeetingSerializer(meetings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_requests(request):
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
def meeting_status_update(request, id):
    student = request.user
    
    try:
        meeting = StudentMeeting.objects.select_related(
            'counselling_user_id', 'studying_user_id'
        ).get(meeting_id=id)
    except StudentMeeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'error': 'Status is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_status == 'accepted':
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
        
        scheduled_time = request.data.get('scheduled_time')
        if scheduled_time:
            try:
                if isinstance(scheduled_time, str):
                    scheduled_time = scheduled_time.replace('Z', '+00:00')
                    scheduled_time = datetime.fromisoformat(scheduled_time)
                if timezone.is_naive(scheduled_time):
                    scheduled_time = timezone.make_aware(scheduled_time)
            except Exception:
                scheduled_time = timezone.now() + timedelta(days=1)
        else:
            scheduled_time = timezone.now() + timedelta(days=1)
        
        meet_link = generate_jitsi_meeting_link(
            meeting.studying_user_id.student_user_id,
            meeting.counselling_user_id.student_user_id
        )
        
        meeting.scheduled_time = scheduled_time
        meeting.duration_minutes = request.data.get('duration_minutes', 30)
        meeting.meet_link = meet_link
        meeting.status = 'accepted'
        meeting.save()
        
        return Response(StudentMeetingSerializer(meeting).data)
    
    elif new_status == 'rejected':
        if student != meeting.studying_user_id:
            return Response(
                {'error': 'Only the studying student can reject meetings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        meeting.status = 'rejected'
        meeting.save()
        return Response(StudentMeetingSerializer(meeting).data)
    
    elif new_status in ['completed', 'cancelled']:
        if student not in [meeting.counselling_user_id, meeting.studying_user_id]:
            return Response(
                {'error': 'You are not authorized to update this meeting'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if new_status == 'cancelled' and meeting.status not in ['requested', 'accepted']:
            return Response(
                {'error': 'Only requested or accepted meetings can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
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
    from colleges.models import Branch
    
    try:
        branch = Branch.objects.get(unique_key=unique_key)
    except Branch.DoesNotExist:
        return Response(
            {'error': 'Branch not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    from reviews.models import CollegeReview
    
    students_with_reviews = Student.objects.filter(
        type_of_student='studying',
        unique_key=branch,
        is_active=True
    ).filter(
        college_reviews__unique_key=branch
    ).distinct()
    
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
