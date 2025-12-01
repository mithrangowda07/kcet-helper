from django.urls import path
from .views import (
    meeting_request, my_requests, my_invitations,
    meeting_status_update, branch_students
)

urlpatterns = [
    path('request/', meeting_request, name='meeting-request'),
    path('my-requests/', my_requests, name='my-requests'),
    path('my-invitations/', my_invitations, name='my-invitations'),
    path('<int:meeting_id>/status/', meeting_status_update, name='meeting-status-update'),
    path('branches/<str:unique_key>/students/', branch_students, name='branch-students'),
]

