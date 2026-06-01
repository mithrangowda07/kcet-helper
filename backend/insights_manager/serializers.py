from rest_framework import serializers

from colleges.models import Branch, College
from colleges.serializers import BranchSerializer, CollegeSerializer
from insights_manager.models import AdminAccount, BranchInsightFile


class AdminCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = [
            'college_id',
            'public_id',
            'college_code',
            'college_name',
            'location',
            'college_link',
        ]


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class AdminAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAccount
        fields = ['id', 'email', 'name', 'is_active', 'created_at']
        read_only_fields = fields


class BranchInsightUploadSerializer(serializers.Serializer):
    college_id = serializers.CharField(max_length=3)
    branch_id = serializers.CharField(max_length=6)
    json_text = serializers.CharField(required=False, allow_blank=True)
    json_file = serializers.FileField(required=False, allow_empty_file=False)

    def validate(self, attrs):
        json_text = (attrs.get('json_text') or '').strip()
        json_file = attrs.get('json_file')

        if not json_text and not json_file:
            raise serializers.ValidationError(
                'Provide either json_text or json_file.'
            )
        if json_text and json_file:
            raise serializers.ValidationError(
                'Provide only one of json_text or json_file, not both.'
            )

        if json_file:
            if json_file.content_type not in ('application/json', 'text/json', 'application/octet-stream'):
                if not str(json_file.name or '').lower().endswith('.json'):
                    raise serializers.ValidationError(
                        {'json_file': 'File must be a JSON file (.json).'}
                    )
            max_bytes = self.context.get('max_upload_bytes', 2 * 1024 * 1024)
            if json_file.size > max_bytes:
                raise serializers.ValidationError(
                    {'json_file': f'File exceeds maximum size of {max_bytes} bytes.'}
                )

        return attrs


class BranchInsightFileSerializer(serializers.ModelSerializer):
    college = CollegeSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = BranchInsightFile
        fields = [
            'id',
            'college',
            'branch',
            's3_url',
            'original_filename',
            'file_size',
            'uploaded_at',
            'is_active',
        ]
        read_only_fields = fields
