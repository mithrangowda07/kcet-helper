from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model
import re
from .models import Student
from colleges.serializers import BranchSerializer


class StudentSerializer(serializers.ModelSerializer):
    unique_key_data = BranchSerializer(source='unique_key', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'student_user_id', 'type_of_student', 'name', 'category', 'unique_key', 'unique_key_data',
            'year_of_starting', 'college_code', 'phone_number', 'email_id',
            'kcet_rank', 'is_active', 'profile_completed', 'created_at', 'last_login'
        ]
        read_only_fields = ['student_user_id', 'created_at', 'last_login']

    def validate(self, attrs):
        """
        Prevent studying students from changing college/branch once set.
        Still allow initial population if missing (legacy users).
        """
        instance = getattr(self, 'instance', None)
        if instance and instance.type_of_student == 'studying':
            # Enforce college_code immutability once present
            if 'college_code' in attrs:
                incoming = attrs.get('college_code')
                current = instance.college_code
                if current and incoming is not None and incoming != current:
                    raise serializers.ValidationError({
                        'college_code': 'Studying students cannot change their college.'
                    })
                if incoming in [None, '']:
                    raise serializers.ValidationError({
                        'college_code': 'College code is required for studying students.'
                    })

            # Enforce unique_key immutability once present
            if 'unique_key' in attrs:
                incoming_branch = attrs.get('unique_key')
                current_branch = instance.unique_key
                if current_branch and incoming_branch is not None and incoming_branch != current_branch:
                    raise serializers.ValidationError({
                        'unique_key': 'Studying students cannot change their branch.'
                    })
                if incoming_branch is None:
                    raise serializers.ValidationError({
                        'unique_key': 'Branch is required for studying students.'
                    })
        return super().validate(attrs)


class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Student
        fields = [
            'type_of_student', 'name', 'category', 'email_id', 'phone_number', 'password', 'password_confirm',
            'kcet_rank', 'college_code', 'unique_key', 'year_of_starting'
        ]

    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError('Password must contain at least one special character')
        
        return value

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


class StudentTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom refresh serializer that returns a clean 401/invalid token error
    instead of a 500 when the user referenced in the refresh token no longer
    exists (e.g. deleted after token issuance).
    """

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id:
            User = get_user_model()
            try:
                user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except User.DoesNotExist:
                # Mirror SimpleJWT behaviour but avoid server error
                raise InvalidToken("No active account found for the given token.")

            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    # Blacklist app not installed
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()

            data["refresh"] = str(refresh)

        return data

