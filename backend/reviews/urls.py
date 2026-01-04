from django.urls import path
from .views import (
    review_create, 
    branch_reviews, 
    college_reviews, 
    my_review, 
    delete_my_review,
    check_text,
    validate_all
)

urlpatterns = [
    path('', review_create, name='review-create'),
    path('check-text/', check_text, name='check-text'),
    path('validate-all/', validate_all, name='validate-all'),
    path('my-review/<str:unique_key>/', my_review, name='my-review'),
    path('my-review/<str:unique_key>/delete/', delete_my_review, name='delete-my-review'),
    path('branches/<uuid:public_id>/', branch_reviews, name='branch-reviews'),
    path('colleges/<uuid:public_id>/', college_reviews, name='college-reviews'),
]

