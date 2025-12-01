from django.contrib import admin
from .models import CounsellingChoice


@admin.register(CounsellingChoice)
class CounsellingChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_id', 'student_user_id', 'order_of_list', 'unique_key', 'created_at')
    search_fields = ('student_user_id__email_id', 'unique_key__branch_name')
    list_filter = ('created_at',)

