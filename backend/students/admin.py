from django.contrib import admin
from .models import Student, StudentCounter


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_user_id', 'email_id', 'type_of_student', 'college_code', 'kcet_rank', 'is_active')
    search_fields = ('student_user_id', 'email_id', 'phone_number')
    list_filter = ('type_of_student', 'is_active', 'profile_completed')
    readonly_fields = ('student_user_id', 'created_at', 'updated_at', 'last_login')


@admin.register(StudentCounter)
class StudentCounterAdmin(admin.ModelAdmin):
    list_display = ('id',)

