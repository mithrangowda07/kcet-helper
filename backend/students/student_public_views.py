from urllib.parse import urlparse

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from insights_manager.services.s3_service import S3ConfigurationError, S3UploadError, upload_student_id_card


ALLOWED_ID_CARD_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'application/pdf',
}
MAX_ID_CARD_BYTES = 10 * 1024 * 1024


def _bucket_name() -> str:
    return getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '') or ''


def validate_id_card_url(url: str) -> bool:
    if not url:
        return False
    bucket = _bucket_name()
    if not bucket:
        return False
    parsed = urlparse(url)
    host = (parsed.netloc or '').lower()
    path = parsed.path or ''
    if bucket in host and 'student-id-cards/' in path:
        return True
    if path.startswith(f'/{bucket}/student-id-cards/'):
        return True
    return 'student-id-cards/' in path


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_id_card(request):
    """
    Upload student ID card to S3 before registration.
    Returns { id_card_url }.
    """
    upload_file = request.FILES.get('file') or request.FILES.get('id_card_image')
    if not upload_file:
        return Response(
            {'error': 'No file provided. Use field name "file" or "id_card_image".'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    content_type = (upload_file.content_type or '').lower()
    filename = upload_file.name or 'id-card'
    if content_type not in ALLOWED_ID_CARD_TYPES:
        lower_name = filename.lower()
        if not lower_name.endswith(('.jpg', '.jpeg', '.png', '.pdf', '.webp')):
            return Response(
                {'error': 'Invalid file type. Allowed: JPG, JPEG, PNG, WEBP, PDF.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if lower_name.endswith('.pdf'):
            content_type = 'application/pdf'
        else:
            content_type = 'image/jpeg'

    if upload_file.size > MAX_ID_CARD_BYTES:
        return Response(
            {'error': 'File too large. Maximum size is 10MB.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        content = upload_file.read()
        result = upload_student_id_card(
            content=content,
            content_type=content_type,
            original_filename=filename,
        )
    except S3ConfigurationError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except S3UploadError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({'id_card_url': result['s3_url']}, status=status.HTTP_201_CREATED)
