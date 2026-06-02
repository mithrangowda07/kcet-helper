from django.urls import path

from students import student_public_views
from students.views import register_studying_student

urlpatterns = [
    path('register/', register_studying_student, name='student-register'),
    path('upload-id-card/', student_public_views.upload_id_card, name='student-upload-id-card'),
]
