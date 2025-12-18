from django.db import models
from students.models import Student


class StudentMeeting(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    meeting_id = models.AutoField(primary_key=True)
    counselling_user_id = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='counselling_meetings',
        db_column='counselling_user_id'
    )
    studying_user_id = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='studying_meetings',
        db_column='studying_user_id'
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    meet_link = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_meetings'
        managed = True

    def __str__(self):
        return f"Meeting {self.meeting_id}: {self.counselling_user_id} -> {self.studying_user_id} ({self.status})"

