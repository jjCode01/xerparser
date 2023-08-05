# xerparser
# validators.py
# Functions to validate data during object initialization

from datetime import datetime

date_format = "%Y-%m-%d %H:%M"

def optional_date(value: str) -> datetime | None:
    if value == "" or value is None:
        return None
    return datetime.strptime(value, date_format)


def optional_float(value: str) -> float | None:
    if value == "" or value is None:
        return None
    return float(value)


def float_or_zero(value: str) -> float:
    if value == "" or value is None:
        return 0.0
    return float(value)


def optional_int(value: str) -> int | None:
    if value == "" or value is None:
        return None
    return int(value)


def int_or_zero(value: str) -> int:
    if value == "" or value is None:
        return 0
    return int(value)


def optional_str(value: str) -> str | None:
    return (value, None)[value == ""]
