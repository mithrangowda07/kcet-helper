from django.urls import path
from .views import register, login, me, update_profile, StudentTokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh/', StudentTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', me, name='me'),
    path('profile/', update_profile, name='update-profile'),
]

