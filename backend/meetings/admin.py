from django.contrib import admin
from .models import StudentMeeting


@admin.register(StudentMeeting)
class StudentMeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'counselling_user_id', 'studying_user_id', 'status', 'scheduled_time', 'meet_link')
    search_fields = ('counselling_user_id__email_id', 'studying_user_id__email_id')
    list_filter = ('status', 'scheduled_time')
    readonly_fields = ('meeting_id', 'created_at', 'updated_at')

