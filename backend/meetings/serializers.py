from rest_framework import serializers
from .models import StudentMeeting
from students.serializers import StudentSerializer


class StudentMeetingSerializer(serializers.ModelSerializer):
    counselling_user_id_data = StudentSerializer(source='counselling_user_id', read_only=True)
    studying_user_id_data = StudentSerializer(source='studying_user_id', read_only=True)
    
    class Meta:
        model = StudentMeeting
        fields = [
            'meeting_id', 'counselling_user_id', 'counselling_user_id_data',
            'studying_user_id', 'studying_user_id_data',
            'scheduled_time', 'duration_minutes', 'meet_link',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['meeting_id', 'created_at', 'updated_at']


class MeetingRequestSerializer(serializers.Serializer):
    studying_user_id = serializers.CharField(required=True)
    counselling_user_id = serializers.CharField(required=False)
