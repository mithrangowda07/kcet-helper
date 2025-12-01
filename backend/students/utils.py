# Custom user authentication backend
from django.contrib.auth.backends import BaseBackend
from .models import Student


class StudentAuthBackend(BaseBackend):
    def authenticate(self, request, email_id=None, password=None, **kwargs):
        try:
            student = Student.objects.get(email_id=email_id, is_active=True)
            if student.check_password(password):
                return student
        except Student.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(pk=user_id)
        except Student.DoesNotExist:
            return None

