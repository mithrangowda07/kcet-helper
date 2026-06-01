import logging
from typing import Any
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3ConfigurationError(RuntimeError):
    pass


class S3UploadError(RuntimeError):
    pass


def _get_required_setting(name: str) -> str:
    value = getattr(settings, name, '') or ''
    if not value:
        raise S3ConfigurationError(f'Missing required setting: {name}')
    return value


def get_s3_client():
    return boto3.client(
        's3',
        region_name=_get_required_setting('AWS_S3_REGION_NAME'),
        aws_access_key_id=_get_required_setting('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=_get_required_setting('AWS_SECRET_ACCESS_KEY'),
    )


def build_s3_key(college_code: str, branch_code: str) -> str:
    return f'branch-insights/{college_code}/{branch_code}/insight.json'


def build_public_url(key: str) -> str:
    bucket = _get_required_setting('AWS_STORAGE_BUCKET_NAME')
    region = _get_required_setting('AWS_S3_REGION_NAME')
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', '') or ''
    if custom_domain:
        return f'https://{custom_domain}/{key}'
    return f'https://{bucket}.s3.{region}.amazonaws.com/{key}'


def upload_insight_json(
    *,
    college_code: str,
    branch_code: str,
    content: bytes,
    content_type: str = 'application/json',
) -> dict[str, str]:
    bucket = _get_required_setting('AWS_STORAGE_BUCKET_NAME')
    key = build_s3_key(college_code, branch_code)
    client = get_s3_client()

    extra_args: dict[str, Any] = {'ContentType': content_type}
    if getattr(settings, 'AWS_S3_DEFAULT_ACL', ''):
        extra_args['ACL'] = settings.AWS_S3_DEFAULT_ACL

    try:
        client.put_object(Bucket=bucket, Key=key, Body=content, **extra_args)
    except (ClientError, BotoCoreError) as exc:
        logger.error('S3 upload failed for key %s: %s', key, exc, exc_info=True)
        raise S3UploadError('Failed to upload insight file to S3.') from exc

    return {'s3_key': key, 's3_url': build_public_url(key)}


def fetch_insight_json(*, s3_key: str | None = None, s3_url: str | None = None) -> bytes:
    bucket = _get_required_setting('AWS_STORAGE_BUCKET_NAME')
    client = get_s3_client()

    key = s3_key
    if not key and s3_url:
        parsed = urlparse(s3_url)
        key = parsed.path.lstrip('/')

    if not key:
        raise S3UploadError('No S3 key or URL provided to fetch insight JSON.')

    try:
        response = client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except (ClientError, BotoCoreError) as exc:
        logger.error('S3 fetch failed for key %s: %s', key, exc, exc_info=True)
        raise S3UploadError('Failed to fetch insight file from S3.') from exc


def generate_presigned_url(s3_key: str, expires_in: int | None = None) -> str:
    bucket = _get_required_setting('AWS_STORAGE_BUCKET_NAME')
    client = get_s3_client()
    expiry = expires_in or getattr(settings, 'AWS_S3_SIGNED_URL_EXPIRY', 3600)
    try:
        return client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': s3_key},
            ExpiresIn=expiry,
        )
    except (ClientError, BotoCoreError) as exc:
        logger.error('Failed to generate presigned URL for %s: %s', s3_key, exc, exc_info=True)
        raise S3UploadError('Failed to generate signed URL for insight file.') from exc
