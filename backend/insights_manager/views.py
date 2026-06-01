import logging

from colleges.models import Branch, College
from colleges.serializers import BranchSerializer
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.backends import TokenBackend

from insights_manager.authentication import AdminJWTAuthentication
from insights_manager.models import AdminAccount
from insights_manager.permissions import IsAdminAccount
from insights_manager.serializers import (
    AdminAccountSerializer,
    AdminCollegeSerializer,
    AdminLoginSerializer,
    BranchInsightFileSerializer,
    BranchInsightUploadSerializer,
)
from insights_manager.services.insights_service import (
    InsightNotFoundError,
    fetch_insights_for_branch,
    upload_branch_insight,
)
from insights_manager.services.s3_service import S3ConfigurationError

logger = logging.getLogger(__name__)


def _create_admin_tokens(admin: AdminAccount) -> dict[str, str]:
    token_backend = TokenBackend(algorithm='HS256', signing_key=settings.SECRET_KEY)
    lifetime = getattr(settings, 'ADMIN_JWT_ACCESS_LIFETIME_SECONDS', 3600 * 8)
    now = timezone.now()
    payload = {
        'admin_id': admin.pk,
        'email': admin.email,
        'token_type': 'admin',
        'iat': int(now.timestamp()),
        'exp': int(now.timestamp()) + lifetime,
    }
    access = token_backend.encode(payload)
    return {'access': access}


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    serializer = AdminLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].strip().lower()
    password = serializer.validated_data['password']

    try:
        admin = AdminAccount.objects.get(email__iexact=email, is_active=True)
    except AdminAccount.DoesNotExist:
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not admin.check_password(password):
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    tokens = _create_admin_tokens(admin)
    return Response(
        {
            'admin': AdminAccountSerializer(admin).data,
            'tokens': tokens,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_me(request):
    return Response({'admin': AdminAccountSerializer(request.user).data})


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_college_list(request):
    colleges = College.objects.all().order_by('college_name')
    serializer = AdminCollegeSerializer(colleges, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_branches_by_college(request, college_id):
    branches = (
        Branch.objects.select_related('college', 'cluster')
        .filter(college_id=college_id)
        .order_by('branch_name')
    )
    if not branches.exists():
        if not College.objects.filter(college_id=college_id).exists():
            return Response({'error': 'College not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAdminAccount])
def admin_upload_branch_insight(request):
    serializer = BranchInsightUploadSerializer(
        data=request.data,
        context={
            'max_upload_bytes': getattr(
                settings,
                'BRANCH_INSIGHT_MAX_UPLOAD_BYTES',
                2 * 1024 * 1024,
            ),
        },
    )
    if not serializer.is_valid():
        return Response(
            {'errors': serializer.errors, 'validation_errors': _flatten_errors(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    college_id = serializer.validated_data['college_id']
    branch_id = serializer.validated_data['branch_id']
    json_text = (serializer.validated_data.get('json_text') or '').strip()
    json_file = serializer.validated_data.get('json_file')

    if json_file:
        raw_payload = json_file.read()
        original_filename = json_file.name
    else:
        raw_payload = json_text.encode('utf-8')
        original_filename = 'pasted.json'

    try:
        record = upload_branch_insight(
            college_id=college_id,
            branch_id=branch_id,
            raw_payload=raw_payload,
            admin=request.user,
            original_filename=original_filename,
        )
    except ValueError as exc:
        message = str(exc)
        return Response(
            {
                'error': 'Validation failed.',
                'validation_errors': message.split('; ') if ';' in message else [message],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except S3ConfigurationError as exc:
        return Response(
            {'error': str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except RuntimeError as exc:
        logger.error('Upload failed: %s', exc, exc_info=True)
        return Response(
            {'error': str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            'message': 'Branch insight uploaded successfully.',
            'insight': BranchInsightFileSerializer(record).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_branch_insight(request, branch_id):
    try:
        branch = Branch.objects.select_related('college').get(unique_key=branch_id)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        insights = fetch_insights_for_branch(branch)
    except InsightNotFoundError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_404_NOT_FOUND)
    except RuntimeError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        logger.exception('Unexpected error fetching branch insights for %s', branch_id)
        return Response(
            {'error': 'Unable to fetch branch insights at the moment. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(insights, status=status.HTTP_200_OK)


def _flatten_errors(errors, prefix='') -> list[str]:
    messages: list[str] = []
    if isinstance(errors, dict):
        for key, value in errors.items():
            path = f'{prefix}.{key}' if prefix else str(key)
            messages.extend(_flatten_errors(value, path))
    elif isinstance(errors, list):
        for item in errors:
            if isinstance(item, (dict, list)):
                messages.extend(_flatten_errors(item, prefix))
            else:
                messages.append(f'{prefix}: {item}' if prefix else str(item))
    else:
        messages.append(f'{prefix}: {errors}' if prefix else str(errors))
    return messages
