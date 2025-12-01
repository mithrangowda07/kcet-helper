from rest_framework import serializers
from .models import CounsellingChoice
from colleges.serializers import BranchSerializer


class CounsellingChoiceSerializer(serializers.ModelSerializer):
    unique_key_data = BranchSerializer(source='unique_key', read_only=True)
    
    class Meta:
        model = CounsellingChoice
        fields = [
            'choice_id', 'student_user_id', 'order_of_list',
            'unique_key', 'unique_key_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['choice_id', 'student_user_id', 'created_at', 'updated_at']


class CounsellingChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounsellingChoice
        fields = ['unique_key', 'order_of_list']

