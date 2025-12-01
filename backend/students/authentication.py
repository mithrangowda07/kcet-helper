"""
Custom JWT authentication for Student model
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Student


class StudentJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
            user = Student.objects.get(pk=user_id, is_active=True)
            return user
        except Student.DoesNotExist:
            raise InvalidToken('User not found or inactive')

