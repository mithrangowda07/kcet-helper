from django.urls import path

from insights_manager import views

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
]
