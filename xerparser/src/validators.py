"""
This module contains functions to validate and transorm data during object initialization.
"""

from datetime import datetime

date_format = "%Y-%m-%d %H:%M"  # date format used by P6 when exporting to an xer file


def optional_date(value: str) -> datetime | None:
    """
    Transform a string to a datetime object or return `None` if
    the string is empty.
    """
    if value == "" or value is None:
        return None
    return datetime.strptime(value, date_format)


def optional_float(value: str) -> float | None:
    """
    Transform a string to a float or return `None` if
    the string is empty.
    """
    if value == "" or value is None:
        return None
    return float(value.replace(",", "."))


def float_or_zero(value: str) -> float:
    """
    Transform a string to a float or return 0.0 if
    the string is empty.
    """
    if value == "" or value is None:
        return 0.0
    return float(value.replace(",", "."))


def optional_int(value: str) -> int | None:
    """
    Transform a string to an integer or return `None` if
    the string is empty.
    """
    if value == "" or value is None:
        return None
    return int(value)


def int_or_zero(value: str) -> int:
    """
    Transform a string to an integer or return 0 if
    the string is empty.
    """
    if value == "" or value is None:
        return 0
    return int(value)


def optional_str(value: str) -> str | None:
    """Transform a string to None if its empty."""
    return (value, None)[value == ""]
