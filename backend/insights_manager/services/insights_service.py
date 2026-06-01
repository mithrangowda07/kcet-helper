import json
import logging

from colleges.models import Branch
from django.db import transaction

from insights_manager.models import AdminAccount, BranchInsightFile
from insights_manager.services.s3_service import S3UploadError, fetch_insight_json, upload_insight_json
from insights_manager.services.validation import (
    entry_to_response_dict,
    parse_json_payload,
    validate_branch_insight_payload,
)

logger = logging.getLogger(__name__)


class InsightNotFoundError(RuntimeError):
    pass


def get_branch_code(branch: Branch) -> str:
    """S3 path segment for branch (uses branch_id as branch code in DB)."""
    return branch.branch_id


def get_active_insight_record(branch: Branch) -> BranchInsightFile | None:
    return (
        BranchInsightFile.objects.filter(branch=branch, is_active=True)
        .select_related('college', 'branch')
        .first()
    )


def fetch_insights_for_branch(branch: Branch) -> dict:
    record = get_active_insight_record(branch)
    if not record:
        raise InsightNotFoundError(
            'Branch insights not configured for this college and branch yet.'
        )

    try:
        raw_bytes = fetch_insight_json(s3_key=record.s3_key, s3_url=record.s3_url)
    except S3UploadError as exc:
        raise RuntimeError(str(exc)) from exc

    try:
        data = parse_json_payload(raw_bytes)
    except ValueError as exc:
        logger.error('Stored insight JSON is invalid for branch %s', branch.unique_key)
        raise RuntimeError('Stored branch insights are invalid.') from exc

    from insights_manager.services.validation import extract_entry

    entry = extract_entry(data)
    validated = validate_branch_insight_payload(
        json.dumps(entry),
        expected_college_name=branch.college.college_name,
        expected_branch_name=branch.branch_name,
    )
    return entry_to_response_dict(validated)


def fetch_insights_by_names(college_name: str, branch_name: str) -> dict:
    from django.utils.text import slugify

    target_college = slugify((college_name or '').strip().lower())
    target_branch = slugify((branch_name or '').strip().lower())

    branches = Branch.objects.select_related('college').all()
    for branch in branches:
        if (
            slugify(branch.college.college_name.strip().lower()) == target_college
            and slugify(branch.branch_name.strip().lower()) == target_branch
        ):
            return fetch_insights_for_branch(branch)

    raise InsightNotFoundError(
        'Branch insights not configured for this college and branch yet.'
    )


@transaction.atomic
def upload_branch_insight(
    *,
    college_id: str,
    branch_id: str,
    raw_payload: str | bytes,
    admin: AdminAccount,
    original_filename: str = '',
) -> BranchInsightFile:
    try:
        branch = Branch.objects.select_related('college').get(
            unique_key=branch_id,
            college_id=college_id,
        )
    except Branch.DoesNotExist as exc:
        raise ValueError('Invalid college_id or branch_id.') from exc

    validated = validate_branch_insight_payload(
        raw_payload,
        expected_college_name=branch.college.college_name,
        expected_branch_name=branch.branch_name,
    )

    canonical_json = json.dumps(
        [validated.model_dump()],
        ensure_ascii=False,
        indent=2,
    ).encode('utf-8')

    college_code = branch.college.college_code
    branch_code = get_branch_code(branch)

    try:
        upload_result = upload_insight_json(
            college_code=college_code,
            branch_code=branch_code,
            content=canonical_json,
        )
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError('Failed to upload insight file to S3.') from exc

    BranchInsightFile.objects.filter(branch=branch, is_active=True).update(is_active=False)

    record = BranchInsightFile.objects.create(
        college=branch.college,
        branch=branch,
        s3_url=upload_result['s3_url'],
        s3_key=upload_result['s3_key'],
        uploaded_by=admin,
        original_filename=original_filename or 'insight.json',
        file_size=len(canonical_json),
        is_active=True,
    )
    return record
