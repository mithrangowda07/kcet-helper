from django.db import models
import uuid


class Cluster(models.Model):
    cluster_code = models.CharField(max_length=1, primary_key=True)
    cluster_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'cluster'
        managed = True

    def __str__(self):
        return f"{self.cluster_code} - {self.cluster_name}"


class College(models.Model):
    college_id = models.CharField(max_length=3, primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    college_code = models.CharField(max_length=10, unique=True)
    college_name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    college_link = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'college'
        managed = True

    def __str__(self):
        return f"{self.college_code} - {self.college_name}"


class Branch(models.Model):
    unique_key = models.CharField(max_length=6, primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, db_column='college_id')
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, db_column='cluster_id')
    branch_id = models.CharField(max_length=2)
    branch_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'branch'
        managed = True

    def __str__(self):
        return f"{self.unique_key} - {self.branch_name}"


class Cutoff(models.Model):
    unique_key = models.ForeignKey(Branch, on_delete=models.CASCADE, db_column='unique_key')
    category = models.CharField(max_length=10)
    cutoff_2022_r1 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2022_r2 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2022_r3 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2023_r1 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2023_r2 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2023_r3 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2024_r1 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2024_r2 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2024_r3 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2025_r1 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2025_r2 = models.CharField(max_length=10, null=True, blank=True)
    cutoff_2025_r3 = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'cutoff'
        unique_together = [['unique_key', 'category']]
        managed = True

    def __str__(self):
        return f"{self.unique_key} - {self.category}"


# Model for excel_import table (if it exists in your database)
# Mark as unmanaged so Django doesn't try to create/modify it
class Category(models.Model):
    category = models.CharField(max_length=10, primary_key=True)
    fall_back = models.CharField(max_length=255)

    class Meta:
        db_table = 'category'
        managed = True

    def __str__(self):
        return f"{self.category} - {self.fall_back}"


class ExcelImport(models.Model):
    """
    Placeholder model for excel_import table.
    Marked as unmanaged - Django will not create/modify this table.
    """
    class Meta:
        db_table = 'excel_import'
        managed = False  # Django won't manage this table
