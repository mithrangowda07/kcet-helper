from rest_framework import serializers
from .models import CollegeReview
from students.serializers import StudentSerializer
from colleges.serializers import BranchSerializer


class CollegeReviewSerializer(serializers.ModelSerializer):
    student_user_id_data = StudentSerializer(source='student_user_id', read_only=True)
    unique_key_data = BranchSerializer(source='unique_key', read_only=True)
    
    class Meta:
        model = CollegeReview
        fields = [
            'review_id', 'student_user_id', 'student_user_id_data',
            'unique_key', 'unique_key_data', 'review_date',
            'teaching_rating', 'teaching_review',
            'courses_rating', 'courses_review',
            'library_rating', 'library_review',
            'research_rating', 'research_review',
            'internship_rating', 'internship_review',
            'infrastructure_rating', 'infrastructure_review',
            'administration_rating', 'administration_review',
            'extracurricular_rating', 'extracurricular_review',
            'safety_rating', 'safety_review',
            'placement_rating', 'placement_review',
            'preferred_day', 'preferred_time',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['review_id', 'student_user_id', 'review_date', 'created_at', 'updated_at']


class CollegeReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeReview
        fields = [
            'unique_key',
            'teaching_rating', 'teaching_review',
            'courses_rating', 'courses_review',
            'library_rating', 'library_review',
            'research_rating', 'research_review',
            'internship_rating', 'internship_review',
            'infrastructure_rating', 'infrastructure_review',
            'administration_rating', 'administration_review',
            'extracurricular_rating', 'extracurricular_review',
            'safety_rating', 'safety_review',
            'placement_rating', 'placement_review',
            'preferred_day', 'preferred_time',
        ]

