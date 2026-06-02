from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from insights_manager.authentication import AdminJWTAuthentication
from insights_manager.permissions import IsAdminAccount
from insights_manager.services.s3_service import S3UploadError, extract_s3_key_from_url, generate_presigned_url
from students.models import Student
from students.serializers import AdminStudentDetailSerializer, AdminStudentListSerializer
from students.services.email_service import (
    send_registration_approved_email,
    send_registration_rejected_email,
)


def _studying_students_queryset():
    return Student.objects.filter(type_of_student='studying').select_related(
        'unique_key',
        'unique_key__college',
        'reviewed_by',
    )


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_student_list(request):
    queryset = _studying_students_queryset()

    status_filter = (request.query_params.get('status') or 'all').lower()
    if status_filter == 'pending':
        queryset = queryset.filter(approval_status=Student.ApprovalStatus.PENDING)
    elif status_filter == 'approved':
        queryset = queryset.filter(approval_status=Student.ApprovalStatus.APPROVED)
    elif status_filter == 'rejected':
        queryset = queryset.filter(approval_status=Student.ApprovalStatus.REJECTED)

    search = (request.query_params.get('search') or '').strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(email_id__icontains=search)
            | Q(college_code__icontains=search)
            | Q(unique_key__college__college_name__icontains=search)
            | Q(usn__icontains=search)
        )

    queryset = queryset.order_by('-created_at')
    serializer = AdminStudentListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_student_detail(request, student_id):
    try:
        student = _studying_students_queryset().get(student_user_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = AdminStudentDetailSerializer(student).data
    if student.id_card_url:
        s3_key = extract_s3_key_from_url(student.id_card_url)
        if s3_key:
            try:
                data['id_card_view_url'] = generate_presigned_url(s3_key)
                data['id_card_download_url'] = generate_presigned_url(s3_key)
            except S3UploadError:
                data['id_card_view_url'] = student.id_card_url
                data['id_card_download_url'] = student.id_card_url
        else:
            data['id_card_view_url'] = student.id_card_url
            data['id_card_download_url'] = student.id_card_url

    return Response(data)


@api_view(['POST'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_student_approve(request, student_id):
    try:
        student = _studying_students_queryset().get(student_user_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    if student.approval_status == Student.ApprovalStatus.APPROVED:
        return Response({'message': 'Student is already approved.'})

    student.approval_status = Student.ApprovalStatus.APPROVED
    student.is_verified_student = True
    student.reviewed_by = request.user
    student.reviewed_at = timezone.now()
    student.rejection_reason = ''
    student.save(
        update_fields=[
            'approval_status',
            'is_verified_student',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
        ]
    )

    try:
        send_registration_approved_email(
            student_name=student.name or 'Student',
            recipient=student.email_id,
        )
    except Exception:
        return Response(
            {
                'message': 'Student approved, but the notification email could not be sent.',
                'student': AdminStudentDetailSerializer(student).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            'message': 'Student approved successfully.',
            'student': AdminStudentDetailSerializer(student).data,
        }
    )


@api_view(['POST'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_student_reject(request, student_id):
    reason = (request.data.get('reason') or '').strip()
    if not reason:
        return Response(
            {'error': 'Rejection reason is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        student = _studying_students_queryset().get(student_user_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    student.approval_status = Student.ApprovalStatus.REJECTED
    student.is_verified_student = False
    student.reviewed_by = request.user
    student.reviewed_at = timezone.now()
    student.rejection_reason = reason
    student.save(
        update_fields=[
            'approval_status',
            'is_verified_student',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
        ]
    )

    try:
        send_registration_rejected_email(
            student_name=student.name or 'Student',
            recipient=student.email_id,
            rejection_reason=reason,
        )
    except Exception:
        return Response(
            {
                'message': 'Student rejected, but the notification email could not be sent.',
                'student': AdminStudentDetailSerializer(student).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            'message': 'Student rejected successfully.',
            'student': AdminStudentDetailSerializer(student).data,
        }
    )
