from django.contrib import admin
from .models import College, Cluster, Branch, Cutoff


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('college_id', 'college_code', 'college_name', 'location')
    search_fields = ('college_code', 'college_name', 'location')


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('cluster_code', 'cluster_name')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('unique_key', 'college', 'cluster', 'branch_id', 'branch_name')
    search_fields = ('unique_key', 'branch_name', 'college__college_name')
    list_filter = ('cluster', 'college')


@admin.register(Cutoff)
class CutoffAdmin(admin.ModelAdmin):
    list_display = ('unique_key', 'category', 'cutoff_2025_r1', 'cutoff_2025_r2', 'cutoff_2025_r3')
    search_fields = ('unique_key__branch_name', 'category')
    list_filter = ('category',)

