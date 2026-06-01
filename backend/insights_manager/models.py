from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from colleges.models import Branch, College


class AdminAccount(models.Model):
    """Platform admin for branch insight uploads (separate from Student auth)."""

    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_account'
        managed = True

    def __str__(self):
        return self.email

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)


class BranchInsightFile(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        db_column='college_id',
        related_name='insight_files',
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        db_column='unique_key',
        related_name='insight_files',
    )
    s3_url = models.URLField(max_length=500)
    s3_key = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        AdminAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_insights',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255, blank=True, default='')
    file_size = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'branch_insight_file'
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=['branch'],
                condition=models.Q(is_active=True),
                name='unique_active_insight_per_branch',
            ),
        ]
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.college_id}/{self.branch_id} ({self.original_filename})'
