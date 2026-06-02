from django.urls import path

from insights_manager import student_approval_views, views

urlpatterns = [
    path('login/', views.admin_login, name='admin-login'),
    path('me/', views.admin_me, name='admin-me'),
    path('colleges/', views.admin_college_list, name='admin-college-list'),
    path(
        'colleges/<str:college_id>/branches/',
        views.admin_branches_by_college,
        name='admin-branches-by-college',
    ),
    path(
        'branch-insights/upload/',
        views.admin_upload_branch_insight,
        name='admin-branch-insight-upload',
    ),
    path('students/', student_approval_views.admin_student_list, name='admin-student-list'),
    path(
        'students/<str:student_id>/',
        student_approval_views.admin_student_detail,
        name='admin-student-detail',
    ),
    path(
        'students/<str:student_id>/approve/',
        student_approval_views.admin_student_approve,
        name='admin-student-approve',
    ),
    path(
        'students/<str:student_id>/reject/',
        student_approval_views.admin_student_reject,
        name='admin-student-reject',
    ),
]
