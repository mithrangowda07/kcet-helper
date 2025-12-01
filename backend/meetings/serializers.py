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
            'status', 'feedback', 'created_at', 'updated_at',
        ]
        read_only_fields = ['meeting_id', 'created_at', 'updated_at']


class StudentMeetingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMeeting
        fields = ['studying_user_id', 'scheduled_time']


class StudentMeetingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['accepted', 'rejected', 'completed', 'cancelled'])
    scheduled_time = serializers.DateTimeField(required=False)

