"""
Deprecated: local JSON loading removed. Use insights_manager.services.insights_service.
"""

from insights_manager.services.insights_service import (
    InsightNotFoundError,
    fetch_insights_by_names as get_branch_insights,
)

__all__ = ['get_branch_insights', 'InsightNotFoundError']
