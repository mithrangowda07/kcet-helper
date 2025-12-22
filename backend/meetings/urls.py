from django.urls import path
from .views import (
    meeting_request, meeting_accept, meeting_reject,
    meeting_cancel, meeting_complete, meetings_upcoming,
    my_requests, my_invitations, meeting_status_update, branch_students
)

urlpatterns = [
    path('request/', meeting_request, name='meeting-request'),
    path('my-requests/', my_requests, name='my-requests'),
    path('my-invitations/', my_invitations, name='my-invitations'),
    path('<int:id>/accept/', meeting_accept, name='meeting-accept'),
    path('<int:id>/reject/', meeting_reject, name='meeting-reject'),
    path('<int:id>/cancel/', meeting_cancel, name='meeting-cancel'),
    path('<int:id>/complete/', meeting_complete, name='meeting-complete'),
    path('<int:id>/status/', meeting_status_update, name='meeting-status-update'),
    path('upcoming/', meetings_upcoming, name='meetings-upcoming'),
    path('branches/<uuid:public_id>/students/', branch_students, name='branch-students'),
]
