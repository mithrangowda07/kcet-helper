from django.urls import path
from .views import (
    college_list, college_detail, branch_detail,
    college_cutoff, branch_cutoff, search, branches_by_college_code, category_list
)

urlpatterns = [
    path('', college_list, name='college-list'),
    path('<str:college_id>/', college_detail, name='college-detail'),
    path('<str:college_id>/cutoff/', college_cutoff, name='college-cutoff'),
    path('search/', search, name='search'),
    path('categories/', category_list, name='category-list'),
]

# Branch URLs for separate routing
branch_urlpatterns = [
    path('by-code/<str:college_code>/', branches_by_college_code, name='branches-by-code'),
    path('<str:unique_key>/', branch_detail, name='branch-detail'),
    path('<str:unique_key>/cutoff/', branch_cutoff, name='branch-cutoff'),
]

