from django.db import models
from students.models import Student
from colleges.models import Branch


class CounsellingChoice(models.Model):
    choice_id = models.AutoField(primary_key=True)
    student_user_id = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        db_column='student_user_id'
    )
    order_of_list = models.IntegerField()
    unique_key = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        db_column='unique_key'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'counselling_choices'
        unique_together = [
            ['student_user_id', 'order_of_list'],
            ['student_user_id', 'unique_key'],
        ]
        managed = True

    def __str__(self):
        return f"Choice {self.order_of_list} for {self.student_user_id}"

