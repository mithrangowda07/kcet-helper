"""
URL configuration for kcet_eduguide project.
"""
from django.contrib import admin
from django.urls import path, include
from colleges.urls import branch_urlpatterns
from colleges.views import search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('students.urls')),
    path('api/colleges/', include('colleges.urls')),
    path('api/branches/', include(branch_urlpatterns)),
    path('api/search/', search, name='global-search'),
    path('api/counselling/', include('counselling.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/meetings/', include('meetings.urls')),
]

