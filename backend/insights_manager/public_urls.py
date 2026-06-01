from django.urls import path

from insights_manager import views

urlpatterns = [
    path(
        '<str:branch_id>/',
        views.get_branch_insight,
        name='branch-insight-detail',
    ),
]
