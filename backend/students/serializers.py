from rest_framework import serializers
from .models import Student
from colleges.serializers import BranchSerializer


class StudentSerializer(serializers.ModelSerializer):
    unique_key_data = BranchSerializer(source='unique_key', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'student_user_id', 'type_of_student', 'unique_key', 'unique_key_data',
            'year_of_starting', 'college_code', 'phone_number', 'email_id',
            'kcet_rank', 'is_active', 'profile_completed', 'created_at', 'last_login'
        ]
        read_only_fields = ['student_user_id', 'created_at', 'last_login']


class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Student
        fields = [
            'type_of_student', 'email_id', 'phone_number', 'password', 'password_confirm',
            'kcet_rank', 'college_code', 'unique_key', 'year_of_starting'
        ]

    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError({
                    'password': 'Passwords do not match'
                })
        
        type_of_student = attrs.get('type_of_student')
        
        if type_of_student == 'counselling':
            kcet_rank = attrs.get('kcet_rank')
            if kcet_rank is None or kcet_rank == '':
                raise serializers.ValidationError({
                    'kcet_rank': 'kcet_rank is required for counselling students'
                })
        elif type_of_student == 'studying':
            college_code = attrs.get('college_code')
            unique_key = attrs.get('unique_key')
            year_of_starting = attrs.get('year_of_starting')
            
            if not college_code or college_code == '':
                raise serializers.ValidationError({
                    'college_code': 'college_code is required for studying students'
                })
            if not unique_key or unique_key == '':
                raise serializers.ValidationError({
                    'unique_key': 'unique_key is required for studying students'
                })
            if year_of_starting is None or year_of_starting == '':
                raise serializers.ValidationError({
                    'year_of_starting': 'year_of_starting is required for studying students'
                })
        elif not type_of_student:
            raise serializers.ValidationError({
                'type_of_student': 'type_of_student is required. Must be either "counselling" or "studying"'
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student


class StudentLoginSerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    password = serializers.CharField(write_only=True)

