from django.urls import path
from .views import (
    recommendations, choices_list, choices_create,
    choices_update, choices_delete
)

urlpatterns = [
    path('recommendations/', recommendations, name='recommendations'),
    path('choices/', choices_list, name='choices-list'),
    path('choices/create/', choices_create, name='choices-create'),
    path('choices/<int:choice_id>/update/', choices_update, name='choices-update'),
    path('choices/<int:choice_id>/delete/', choices_delete, name='choices-delete'),
]

