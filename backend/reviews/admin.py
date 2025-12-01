from django.contrib import admin
from .models import CollegeReview


@admin.register(CollegeReview)
class CollegeReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'student_user_id', 'unique_key', 'review_date', 'placement_rating')
    search_fields = ('student_user_id__email_id', 'unique_key__branch_name')
    list_filter = ('review_date',)
    readonly_fields = ('review_id', 'created_at', 'updated_at')

