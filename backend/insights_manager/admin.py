from django.contrib import admin

from insights_manager.models import AdminAccount, BranchInsightFile


@admin.register(AdminAccount)
class AdminAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at')
    search_fields = ('email', 'name')


@admin.register(BranchInsightFile)
class BranchInsightFileAdmin(admin.ModelAdmin):
    list_display = (
        'branch',
        'college',
        'is_active',
        'original_filename',
        'file_size',
        'uploaded_at',
    )
    list_filter = ('is_active', 'college')
    search_fields = ('branch__unique_key', 'college__college_code', 's3_key')
