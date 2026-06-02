"""
URL configuration for kcet_eduguide project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect, JsonResponse
from colleges.urls import branch_urlpatterns
from colleges.views import search

def api_root(request):
    return JsonResponse({
        "auth": "/api/auth/",
        "colleges": "/api/colleges/",
        "branches": "/api/branches/",
        "search": "/api/search/?query=<text>",
        "counselling": "/api/counselling/",
        "reviews": "/api/reviews/",
        "meetings": "/api/meetings/",
        "branch_insights": "/api/branch-insights/<branch_id>/",
        "admin": "/api/admin/",
    })
urlpatterns = [
    path('', lambda request: HttpResponseRedirect('/api/')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('students.urls')),
    path('api/student/', include('students.student_urls')),
    path('api/colleges/', include('colleges.urls')),
    path('api/branches/', include(branch_urlpatterns)),
    path('api/search/', search, name='global-search'),
    path('api/counselling/', include('counselling.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/admin/', include('insights_manager.urls')),
    path('api/branch-insights/', include('insights_manager.public_urls')),
]

