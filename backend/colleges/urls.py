from django.urls import path
from .views import (
    college_list,
    college_detail,
    branch_detail,
    college_cutoff,
    branch_cutoff,
    search,
    branches_by_college_code,
    category_list,
    locations_list,
    cluster_list,
    branch_insights,
)

urlpatterns = [
    path('', college_list, name='college-list'),
    path('categories/', category_list, name='category-list'),
    path('clusters/', cluster_list, name='cluster-list'),
    path('search/', search, name='search'),
    path('locations/', locations_list, name='location-list'),
    path('branch-insights/', branch_insights, name='branch-insights'),
    path('<uuid:public_id>/cutoff/', college_cutoff, name='college-cutoff'),
    path('<uuid:public_id>/', college_detail, name='college-detail'),
]

# Branch URLs for separate routing
branch_urlpatterns = [
    path('by-code/<str:college_code>/', branches_by_college_code, name='branches-by-code'),
    path('<uuid:public_id>/', branch_detail, name='branch-detail'),
    path('<uuid:public_id>/cutoff/', branch_cutoff, name='branch-cutoff'),
]

