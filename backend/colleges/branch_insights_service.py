import json
import logging
import os
from typing import Any, Dict, List

from django.conf import settings
from django.utils.text import slugify

logger = logging.getLogger(__name__)


DATA_FILE_NAME = "about_branch.json"


def _normalize(text: str) -> str:
    return slugify((text or "").strip().lower())


def _load_static_data() -> Any:
    """
    Load static branch insights from backend/data_about.json.
    Supports either:
      - a list of entries
      - an object keyed by some string, with entry objects as values
    """
    base_dir = getattr(settings, "BASE_DIR", os.path.dirname(os.path.dirname(__file__)))
    data_path = os.path.join(base_dir, DATA_FILE_NAME)

    if not os.path.exists(data_path):
        logger.error("Branch insights data file not found at %s", data_path)
        raise RuntimeError(
            "Branch insights data file is missing. Please add backend/data_about.json."
        )

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Failed to load branch insights data: %s", exc, exc_info=True)
        raise RuntimeError("Unable to load branch insights data.") from exc


def _find_entry(college_name: str, branch_name: str) -> Dict[str, Any] | None:
    data = _load_static_data()

    target_college = _normalize(college_name)
    target_branch = _normalize(branch_name)

    # Case 1: list of entries
    if isinstance(data, list):
        for entry in data:
            if not isinstance(entry, dict):
                continue
            c = _normalize(str(entry.get("college_name", "")))
            b = _normalize(str(entry.get("branch_name", "")))
            if c == target_college and b == target_branch:
                return entry
        return None

    # Case 2: object with values as entries
    if isinstance(data, dict):
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            c = _normalize(str(entry.get("college_name", "")))
            b = _normalize(str(entry.get("branch_name", "")))
            if c == target_college and b == target_branch:
                return entry

    return None


def get_branch_insights(college_name: str, branch_name: str) -> Dict[str, Any]:
    """
    Fetch branch insights from static JSON (data_about.json) for the
    requested college + branch.

    Expected entry shape:
      {
        "college_name": "...",
        "branch_name": "...",
        "about": "string",
        "admission_cutoffs": "string",
        "placements": "string",
        "pros_cons": { "pros": [...], "cons": [...] },
        "features": [...],
        "one_line_summary": "string",
        "additional_info": [...]
      }
    """
    entry = _find_entry(college_name, branch_name)
    if not entry:
        raise RuntimeError(
            "Branch insights not configured for this college and branch yet."
        )

    pros_cons = entry.get("pros_cons") or {}

    return {
        "about": entry.get("about", "").strip(),
        "admission_cutoffs": entry.get("admission_cutoffs", "").strip(),
        "placements": entry.get("placements", "").strip(),
        "pros_cons": {
            "pros": list(pros_cons.get("pros", [])),
            "cons": list(pros_cons.get("cons", [])),
        },
        "features": list(entry.get("features", [])),
        "one_line_summary": entry.get("one_line_summary", "").strip(),
        "additional_info": list(entry.get("additional_info", [])),
    }


