"""Reusable text-match helper for search queries.

Provides a MatchMode enum and apply_text_match() that translates a user-supplied
matching strategy into the correct SQLAlchemy column expression.

Design:
  - Enum-controlled — new modes can be added here without touching callers.
  - All comparisons are case-insensitive via ilike / lowercase comparison.
  - Used by IndicatorSearchService and GlobalSearchService.
"""

from __future__ import annotations

import enum

from sqlalchemy import BinaryExpression


class MatchMode(str, enum.Enum):
    """How a text filter value is matched against a column."""

    EXACT = "exact"       # col = value  (case-insensitive via ilike "value")
    PREFIX = "prefix"     # col ilike "value%"
    CONTAINS = "contains" # col ilike "%value%"  — default


def apply_text_match(column, value: str, mode: MatchMode) -> BinaryExpression:
    """Return a SQLAlchemy filter expression for the given match mode.

    Args:
        column: SQLAlchemy mapped column (e.g. Indicator.value).
        value:  The string to match against.
        mode:   MatchMode controlling how the comparison is performed.

    Returns:
        A SQLAlchemy binary expression suitable for use in .filter().
    """
    if mode is MatchMode.EXACT:
        return column.ilike(value)
    if mode is MatchMode.PREFIX:
        return column.ilike(f"{value}%")
    # Default: CONTAINS
    return column.ilike(f"%{value}%")
