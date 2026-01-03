"""
Custom JWT authentication for Student model
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework import exceptions
from .models import Student
import logging

logger = logging.getLogger(__name__)


class StudentJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override to use student_user_id instead of default id field
        """
        try:
            # Get user_id from token payload
            user_id = validated_token.get('user_id')
            if not user_id:
                logger.error('Token missing user_id claim. Token payload: %s', validated_token)
                raise InvalidToken('Token missing user_id claim')
            
            # Look up student using student_user_id as primary key
            try:
                user = Student.objects.get(student_user_id=user_id, is_active=True)
                logger.debug('Successfully authenticated student: %s', user_id)
                return user
            except Student.DoesNotExist:
                logger.error('Student not found with student_user_id: %s', user_id)
                raise InvalidToken('User not found or inactive')
            except Exception as e:
                logger.error('Error retrieving student with student_user_id %s: %s', user_id, str(e))
                raise InvalidToken(f'Error retrieving user: {str(e)}')
        except InvalidToken:
            # Re-raise InvalidToken exceptions
            raise
        except Exception as e:
            # Catch any other exceptions and convert to InvalidToken
            logger.error('Unexpected error in authentication: %s', str(e), exc_info=True)
            raise InvalidToken(f'Authentication failed: {str(e)}')
    
    def authenticate(self, request):
        """
        Override authenticate to add better error handling
        """
        try:
            return super().authenticate(request)
        except InvalidToken as e:
            logger.warning('Invalid token: %s', str(e))
            raise
        except Exception as e:
            logger.error('Authentication error: %s', str(e), exc_info=True)
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

