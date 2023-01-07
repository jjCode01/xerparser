# xerparser
# validators.py
# Functions to validate data during object initialization

from datetime import datetime
from xerparser.schemas.rsrc import RSRC

date_format = "%Y-%m-%d %H:%M"


def datetime_or_none(value: str) -> datetime | None:
    if value == "" or value is None:
        return None
    return datetime.strptime(value, date_format)


def float_or_none(value: str) -> float | None:
    if value == "" or value is None:
        return None
    return float(value)


def float_or_zero(value: str) -> float:
    if value == "" or value is None:
        return 0.0
    return float(value)


def int_or_none(value: str) -> int | None:
    if value == "" or value is None:
        return None
    return int(value)


def rsrc_or_none(value: RSRC | None) -> RSRC | None:
    if value is None:
        return None
    if not isinstance(value, RSRC):
        raise ValueError(f"ValueError: expected <class RSRC>; got {type(value)}")
    return value


def str_or_none(value: str) -> str | None:
    return (value, None)[value == ""]
