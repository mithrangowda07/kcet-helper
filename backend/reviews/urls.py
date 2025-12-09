from django.urls import path
from .views import review_create, branch_reviews, college_reviews, my_review, delete_my_review

urlpatterns = [
    path('', review_create, name='review-create'),
    path('my-review/<str:unique_key>/', my_review, name='my-review'),
    path('my-review/<str:unique_key>/delete/', delete_my_review, name='delete-my-review'),
    path('branches/<str:unique_key>/', branch_reviews, name='branch-reviews'),
    path('colleges/<str:college_id>/', college_reviews, name='college-reviews'),
]

