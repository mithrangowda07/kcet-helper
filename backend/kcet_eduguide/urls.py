"""
URL configuration for kcet_eduguide project.
"""
from django.contrib import admin
from django.urls import path, include
from colleges.urls import branch_urlpatterns
from colleges.views import search
from django.http import HttpResponseRedirect

def api_root(request):
    return JsonResponse({
        "auth": "/api/auth/",
        "colleges": "/api/colleges/",
        "branches": "/api/branches/",
        "search": "/api/search/?query=<text>",
        "counselling": "/api/counselling/",
        "reviews": "/api/reviews/",
        "meetings": "/api/meetings/",
    })
urlpatterns = [
    path('', lambda request: HttpResponseRedirect('/api/')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('students.urls')),
    path('api/colleges/', include('colleges.urls')),
    path('api/branches/', include(branch_urlpatterns)),
    path('api/search/', search, name='global-search'),
    path('api/counselling/', include('counselling.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/meetings/', include('meetings.urls')),
]

