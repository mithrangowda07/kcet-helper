from django.urls import path
from .views import (
    college_list, college_detail, branch_detail,
    college_cutoff, branch_cutoff, search
)

urlpatterns = [
    path('', college_list, name='college-list'),
    path('<str:college_id>/', college_detail, name='college-detail'),
    path('<str:college_id>/cutoff/', college_cutoff, name='college-cutoff'),
    path('search/', search, name='search'),
]

# Branch URLs for separate routing
branch_urlpatterns = [
    path('<str:unique_key>/', branch_detail, name='branch-detail'),
    path('<str:unique_key>/cutoff/', branch_cutoff, name='branch-cutoff'),
]

