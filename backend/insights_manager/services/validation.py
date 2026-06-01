import json
from typing import Any

from django.utils.text import slugify
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class ProsConsSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    pros: list[str]
    cons: list[str]

    @field_validator('pros', 'cons')
    @classmethod
    def must_be_string_lists(cls, value: list[str]) -> list[str]:
        if not isinstance(value, list):
            raise ValueError('must be a list')
        for item in value:
            if not isinstance(item, str):
                raise ValueError('all items must be strings')
        return value


class BranchInsightEntrySchema(BaseModel):
    """Exact schema for a single branch insight entry."""

    model_config = ConfigDict(extra='forbid')

    college_name: str
    branch_name: str
    about: str
    admission_cutoffs: str
    placements: str
    pros_cons: ProsConsSchema
    features: list[str]
    one_line_summary: str
    additional_info: list[str]

    @field_validator(
        'college_name',
        'branch_name',
        'about',
        'admission_cutoffs',
        'placements',
        'one_line_summary',
    )
    @classmethod
    def must_be_non_empty_strings(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError('must be a non-empty string')
        return value

    @field_validator('features', 'additional_info')
    @classmethod
    def must_be_string_lists(cls, value: list[str]) -> list[str]:
        if not isinstance(value, list):
            raise ValueError('must be a list')
        for item in value:
            if not isinstance(item, str):
                raise ValueError('all items must be strings')
        return value


def _normalize_name(text: str) -> str:
    return slugify((text or '').strip().lower())


def format_validation_errors(exc: ValidationError) -> list[str]:
    messages: list[str] = []
    for error in exc.errors():
        location = '.'.join(str(part) for part in error.get('loc', ()))
        messages.append(f'{location}: {error.get("msg", "invalid value")}')
    return messages


def parse_json_payload(raw: str | bytes) -> Any:
    if isinstance(raw, bytes):
        text = raw.decode('utf-8')
    else:
        text = raw
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Invalid JSON syntax: {exc.msg} at line {exc.lineno}, column {exc.colno}') from exc


def extract_entry(data: Any) -> dict[str, Any]:
    """Accept a single object or a one-element array matching the sample format."""
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError('JSON array must contain at least one entry.')
        if len(data) > 1:
            raise ValueError(
                'JSON array must contain exactly one entry when uploading for a single branch.'
            )
        entry = data[0]
        if not isinstance(entry, dict):
            raise ValueError('Array entry must be an object.')
        return entry
    raise ValueError('JSON must be an object or an array of objects.')


def validate_branch_insight_payload(
    raw: str | bytes,
    *,
    expected_college_name: str,
    expected_branch_name: str,
) -> BranchInsightEntrySchema:
    data = parse_json_payload(raw)
    entry = extract_entry(data)

    try:
        validated = BranchInsightEntrySchema.model_validate(entry)
    except ValidationError as exc:
        raise ValueError('; '.join(format_validation_errors(exc))) from exc

    if _normalize_name(validated.college_name) != _normalize_name(expected_college_name):
        raise ValueError(
            f'college_name must match selected college ({expected_college_name!r}).'
        )
    if _normalize_name(validated.branch_name) != _normalize_name(expected_branch_name):
        raise ValueError(
            f'branch_name must match selected branch ({expected_branch_name!r}).'
        )

    return validated


def entry_to_response_dict(entry: BranchInsightEntrySchema | dict[str, Any]) -> dict[str, Any]:
    if isinstance(entry, BranchInsightEntrySchema):
        data = entry.model_dump()
    else:
        data = entry

    pros_cons = data.get('pros_cons') or {}
    return {
        'about': str(data.get('about', '')).strip(),
        'admission_cutoffs': str(data.get('admission_cutoffs', '')).strip(),
        'placements': str(data.get('placements', '')).strip(),
        'pros_cons': {
            'pros': list(pros_cons.get('pros', [])),
            'cons': list(pros_cons.get('cons', [])),
        },
        'features': list(data.get('features', [])),
        'one_line_summary': str(data.get('one_line_summary', '')).strip(),
        'additional_info': list(data.get('additional_info', [])),
    }
