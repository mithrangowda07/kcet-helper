from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError
from .models import Student
from .serializers import (
    StudentSerializer,
    StudentRegisterSerializer,
    StudentLoginSerializer,
    StudentTokenRefreshSerializer,
    StudentVerificationSerializer,
    CounsellingStudentRegisterSerializer,
    StudyingStudentRegisterSerializer,
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.db import transaction
from colleges.models import College


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = StudentRegisterSerializer(data=request.data)
    if serializer.is_valid():
        # ✅ EARLY EXIT - Check if email exists BEFORE attempting to create
        # This prevents IntegrityError and duplicate insert attempts in most cases
        # Email is already normalized to lowercase in serializer.validate_email_id()
        email_id = serializer.validated_data.get('email_id', '').strip().lower()
        
        # Check if email already exists (email is normalized, so direct comparison is safe)
        if Student.objects.filter(email_id__iexact=email_id).exists():
            return Response({
                'error': 'Email already registered',
                'message': 'An account with this email already exists. Please use a different email or try logging in.',
                'field': 'email_id'
            }, status=status.HTTP_409_CONFLICT)
        
        # Note: USN duplicate check is already handled in serializer.validate()
        # No need to check again here
        
        # ✅ CREATE WITH INTEGRITY ERROR HANDLING - Protects against race conditions
        try:
            type_of_student = serializer.validated_data.get('type_of_student')
            student = serializer.save()
            
            # For studying students, set is_verified_student after creation
            # (verification was done before registration)
            if type_of_student == 'studying':
                student.approval_status = Student.ApprovalStatus.PENDING
                student.is_verified_student = False
                student.save()
            
            student_data = StudentSerializer(student).data
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(student)
            
            return Response({
                'student': student_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            # Handle database integrity errors (duplicate email, USN, etc.)
            # MySQL error format: (1062, "Duplicate entry 'value' for key 'table.field'")
            error_message = str(e.args[0]) if e.args else str(e)
            error_message_lower = error_message.lower()
            
            # Check if it's a duplicate email error - check for email_id key in error
            if 'email_id' in error_message_lower or '.email_id' in error_message_lower:
                # Verify email exists now (might have been inserted by concurrent request)
                # Email is normalized, so direct comparison is safe
                if Student.objects.filter(email_id__iexact=email_id).exists():
                    return Response({
                        'error': 'Email already registered',
                        'message': 'An account with this email already exists. Please use a different email or try logging in.',
                        'field': 'email_id'
                    }, status=status.HTTP_409_CONFLICT)
                else:
                    # Edge case: integrity error but email doesn't exist (shouldn't happen)
                    return Response({
                        'error': 'Registration conflict',
                        'message': 'A registration conflict occurred. Please try again.',
                    }, status=status.HTTP_409_CONFLICT)
            
            # Check if it's a duplicate USN error - check for usn key in error
            if 'usn' in error_message_lower and '.usn' in error_message_lower:
                return Response({
                    'error': 'USN already registered',
                    'message': 'This USN/Student ID is already registered. Please use a different USN.',
                    'field': 'usn'
                }, status=status.HTTP_409_CONFLICT)
            
            # Generic integrity error (shouldn't happen with proper validation)
            # Check if email exists as fallback (race condition protection)
            # Email is normalized, so direct comparison is safe
            if Student.objects.filter(email_id__iexact=email_id).exists():
                return Response({
                    'error': 'Email already registered',
                    'message': 'An account with this email already exists. Please use a different email or try logging in.',
                    'field': 'email_id'
                }, status=status.HTTP_409_CONFLICT)
            
            # Log unexpected integrity error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"IntegrityError during registration: {error_message}", exc_info=False)
            
            return Response({
                'error': 'Registration conflict',
                'message': 'A conflict occurred during registration. Please check your information and try again.',
            }, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            # Handle all other unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
            
            return Response({
                'error': 'Error creating student account',
                'message': 'An unexpected error occurred. Please try again.',
                'detail': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Return detailed validation errors
    return Response({
        'errors': serializer.errors,
        'message': 'Validation failed. Please check the errors below.'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = StudentLoginSerializer(data=request.data)
    if serializer.is_valid():
        email_id = serializer.validated_data['email_id']
        password = serializer.validated_data['password']
        
        try:
            student = Student.objects.get(email_id=email_id, is_active=True)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not student.check_password(password):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        if student.type_of_student == 'studying':
            if student.approval_status == Student.ApprovalStatus.PENDING:
                return Response(
                    {
                        'error': 'Account pending approval',
                        'message': (
                            'Your registration is pending administrator approval. '
                            'You will receive an email once your application has been reviewed.'
                        ),
                        'approval_status': student.approval_status,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            if student.approval_status == Student.ApprovalStatus.REJECTED:
                return Response(
                    {
                        'error': 'Registration rejected',
                        'message': 'Your student registration was rejected.',
                        'approval_status': student.approval_status,
                        'rejection_reason': student.rejection_reason,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        
        # Update last_login
        student.last_login = timezone.now()
        student.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(student)
        student_data = StudentSerializer(student).data
        
        return Response({
            'student': student_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    student = request.user
    serializer = StudentSerializer(student)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update student profile"""
    student = request.user
    serializer = StudentSerializer(student, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentTokenRefreshView(TokenRefreshView):
    """
    Override to plug in StudentTokenRefreshSerializer so missing users result
    in a clean 401 instead of a server error.
    """

    serializer_class = StudentTokenRefreshSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_student(request):
    """Deprecated: OCR ID verification removed in favor of manual admin approval."""
    return Response(
        {
            'error': 'ID card scanning has been removed.',
            'message': 'Upload your student ID card during registration for admin review.',
        },
        status=status.HTTP_410_GONE,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_counselling_student(request):
    """
    Register a counselling student - simple flow without verification.
    """
    serializer = CounsellingStudentRegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'errors': serializer.errors,
            'message': 'Validation failed. Please check the errors below.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email_id = serializer.validated_data.get('email_id', '').strip().lower()
    
    # Check if email already exists
    if Student.objects.filter(email_id__iexact=email_id).exists():
        return Response({
            'error': 'Email already registered',
            'message': 'An account with this email already exists. Please use a different email or try logging in.',
            'field': 'email_id'
        }, status=status.HTTP_409_CONFLICT)
    
    try:
        student = serializer.save()
        student_data = StudentSerializer(student).data
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(student)
        
        return Response({
            'student': student_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        error_message = str(e.args[0]) if e.args else str(e)
        error_message_lower = error_message.lower()
        
        if 'email_id' in error_message_lower or '.email_id' in error_message_lower:
            if Student.objects.filter(email_id__iexact=email_id).exists():
                return Response({
                    'error': 'Email already registered',
                    'message': 'An account with this email already exists. Please use a different email or try logging in.',
                    'field': 'email_id'
                }, status=status.HTTP_409_CONFLICT)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"IntegrityError during counselling registration: {error_message}", exc_info=False)
        
        return Response({
            'error': 'Registration conflict',
            'message': 'A conflict occurred during registration. Please check your information and try again.',
        }, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
        
        return Response({
            'error': 'Error creating student account',
            'message': 'An unexpected error occurred. Please try again.',
            'detail': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def register_studying_student(request):
    """
    Register a studying student with a pre-uploaded ID card URL (S3).
    Account is created in PENDING approval state; no JWT is issued.
    """
    serializer = StudyingStudentRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'errors': serializer.errors,
            'message': 'Validation failed. Please check the errors below.'
        }, status=status.HTTP_400_BAD_REQUEST)

    email_id = serializer.validated_data.get('email_id', '').strip().lower()
    usn = serializer.validated_data.get('usn', '')

    if Student.objects.filter(email_id__iexact=email_id).exists():
        return Response({
            'error': 'Email already registered',
            'message': 'An account with this email already exists. Please use a different email or try logging in.',
            'field': 'email_id'
        }, status=status.HTTP_409_CONFLICT)

    try:
        validated_data = serializer.validated_data.copy()
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        validated_data['email_id'] = validated_data['email_id'].strip().lower()
        validated_data['type_of_student'] = 'studying'
        validated_data['approval_status'] = Student.ApprovalStatus.PENDING
        validated_data['is_verified_student'] = False

        student = Student(**validated_data)
        student.set_password(password)
        student.save()

        student_data = StudentSerializer(student).data

        return Response({
            'student': student_data,
            'approval_status': student.approval_status,
            'message': (
                'Registration submitted successfully.\n\n'
                'Your account is pending administrator approval.\n'
                'You will receive an email once your application has been reviewed.'
            ),
        }, status=status.HTTP_201_CREATED)

    except IntegrityError as e:
        # Rollback is automatic with @transaction.atomic
        error_message = str(e.args[0]) if e.args else str(e)
        error_message_lower = error_message.lower()
        
        if 'email_id' in error_message_lower or '.email_id' in error_message_lower:
            if Student.objects.filter(email_id__iexact=email_id).exists():
                return Response({
                    'error': 'Email already registered',
                    'message': 'An account with this email already exists. Please use a different email or try logging in.',
                    'field': 'email_id'
                }, status=status.HTTP_409_CONFLICT)
        
        if 'usn' in error_message_lower and '.usn' in error_message_lower:
            return Response({
                'error': 'USN already registered',
                'message': 'This USN/Student ID is already registered. Please use a different USN.',
                'field': 'usn'
            }, status=status.HTTP_409_CONFLICT)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"IntegrityError during studying registration: {error_message}", exc_info=False)
        
        return Response({
            'error': 'Registration conflict',
            'message': 'A conflict occurred during registration. Please check your information and try again.',
        }, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        # Rollback is automatic with @transaction.atomic
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
        
        return Response({
            'error': 'Error creating student account',
            'message': 'An unexpected error occurred. Please try again.',
            'detail': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
