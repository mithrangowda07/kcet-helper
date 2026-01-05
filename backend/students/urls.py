from django.urls import path
from .views import (
    register, login, me, update_profile, StudentTokenRefreshView, verify_student,
    register_counselling_student, register_studying_student
)

urlpatterns = [
    # Legacy registration endpoint (kept for backward compatibility)
    path('register/', register, name='register'),
    # New separate registration endpoints
    path('register/counselling/', register_counselling_student, name='register-counselling'),
    path('register/studying/', register_studying_student, name='register-studying'),
    path('login/', login, name='login'),
    path('refresh/', StudentTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', me, name='me'),
    path('profile/', update_profile, name='update-profile'),
    path('student/verify/', verify_student, name='verify-student'),
]

