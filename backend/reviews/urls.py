from django.urls import path
from .views import review_create, branch_reviews, college_reviews

urlpatterns = [
    path('', review_create, name='review-create'),
    path('branches/<str:unique_key>/', branch_reviews, name='branch-reviews'),
    path('colleges/<str:college_id>/', college_reviews, name='college-reviews'),
]

