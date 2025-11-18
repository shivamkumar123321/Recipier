"""
Date and time utility functions.
"""

from datetime import datetime, timezone
from typing import Optional


def get_current_utc() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime object to format
        format: Format string (default: ISO-like format)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format)


def parse_datetime(
    date_string: str,
    format: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse datetime string to datetime object.

    Args:
        date_string: String to parse
        format: Format string to use for parsing

    Returns:
        Parsed datetime object, or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None
