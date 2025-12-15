from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from .models import Student
from .serializers import (
    StudentSerializer,
    StudentRegisterSerializer,
    StudentLoginSerializer,
    StudentTokenRefreshSerializer,
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = StudentRegisterSerializer(data=request.data)
    if serializer.is_valid():
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
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e),
                'detail': 'Error creating student account'
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
