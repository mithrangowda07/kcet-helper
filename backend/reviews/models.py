from django.db import models
from students.models import Student
from colleges.models import Branch


class CollegeReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    student_user_id = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        db_column='student_user_id'
    )
    unique_key = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        db_column='unique_key'
    )
    review_date = models.DateTimeField(auto_now_add=True)
    
    # Rating fields (1-5 scale)
    teaching_rating = models.SmallIntegerField()
    courses_rating = models.SmallIntegerField()
    library_rating = models.SmallIntegerField()
    research_rating = models.SmallIntegerField()
    internship_rating = models.SmallIntegerField()
    infrastructure_rating = models.SmallIntegerField()
    administration_rating = models.SmallIntegerField()
    extracurricular_rating = models.SmallIntegerField()
    safety_rating = models.SmallIntegerField()
    placement_rating = models.SmallIntegerField()
    
    # Review text fields
    teaching_review = models.TextField(blank=True)
    courses_review = models.TextField(blank=True)
    library_review = models.TextField(blank=True)
    research_review = models.TextField(blank=True)
    internship_review = models.TextField(blank=True)
    infrastructure_review = models.TextField(blank=True)
    administration_review = models.TextField(blank=True)
    extracurricular_review = models.TextField(blank=True)
    safety_review = models.TextField(blank=True)
    placement_review = models.TextField(blank=True)
    
    preferred_day = models.CharField(max_length=100, blank=True)
    preferred_time = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'college_reviews'
        unique_together = [['student_user_id', 'unique_key']]
        managed = True

    def __str__(self):
        return f"Review {self.review_id} by {self.student_user_id} for {self.unique_key}"

