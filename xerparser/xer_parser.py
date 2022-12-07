# xerparser
# xer_parser.py

from datetime import datetime

__all__ = ("xer_to_dict",)

CODEC = "cp1252"


def xer_to_dict(file: bytes | str) -> dict:
    """Reads a P6 .xer file and converts it into a Python dictionary object.
    Args:
        file (bytes | str): .xer file exported from P6.
    Returns:
        dict: Dictionary of the xer information and data tables
    """
    xer_data = {}
    table_list = _parse_file_to_list_of_tables(file)

    # The first row in the xer file includes information about the file
    version, export_date = table_list.pop(0).strip().split("\t")[1:3]
    xer_data["version"] = version
    xer_data["export_date"] = datetime.strptime(export_date, "%Y-%m-%d")

    tables = {
        name: rows for table in table_list for name, rows in _parse_table(table).items()
    }

    xer_data["tables"] = tables
    xer_data["errors"] = _find_xer_errors(tables)

    return xer_data


def _parse_file_to_list_of_tables(file) -> list[str]:
    """
    Read file and verify it is a valid XER. Parse file into a list of tables.
    """

    # TODO: Add ability to read UploadFile from fastapi.
    file_as_str = ""

    if isinstance(file, bytes):
        file_as_str = file.decode(CODEC, errors="ignore")
    elif isinstance(file, str):
        with open(file, encoding=CODEC, errors="ignore") as f:
            file_as_str = f.read()
    else:
        # File is type ???
        try:
            file_as_str = file.read().decode(CODEC, errors="ignore")
        except:
            raise ValueError("Cannot Read File")

    return _verify_file(file_as_str)


def _verify_file(_file: str) -> list[str]:
    if not _file.startswith("ERMHDR"):
        raise ValueError(f"ValueError: invalid XER file")

    return _file.split("%T\t")


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines = table.split("\n")
    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).split("\t")[1:]  # Second line is the column labels
    table = {
        name: [
            _row_to_dict(cols, line.split("\t")[1:])
            for line in lines
            if line and not line.startswith("%E")
        ]
    }
    return table


def _row_to_dict(columns: list[str, str], values: list) -> dict[str, str]:
    """Convert row of values to dictionary objects"""

    return {
        key.strip(): _empty_str_to_none(val) for key, val in tuple(zip(columns, values))
    }


def _empty_str_to_none(value: str) -> str | None:
    """
    Convert empty strings to type None.
    For projects using pydantic, which does not automatically convert
    empty strings to None and causes an error when creating a BaseModel schema.
    """
    if value == "":
        return None

    return value


def _find_xer_errors(tables: dict) -> list[str]:
    """
    Find issues with the xer file, including
    - Missing tables
    - Non-existent calendars assigned to activities
    """
    # This list of required tables may be subjective
    # TODO: Add ability to pass in your own list of required tables.
    REQUIRED_TABLES = ("CALENDAR", "PROJECT", "PROJWBS", "TASK", "TASKPRED")

    REQUIRED_TABLE_PAIRS = {
        "TASKFIN": "FINDATES",
        "TRSRCFIN": "FINDATES",
        "TASKRSRC": "RSRC",
        "TASKMEMO": "MEMOTYPE",
        "ACTVCODE": "ACTVTYPE",
        "TASKACTV": "ACTVCODE",
    }

    errors = []

    # Check for minimum tables required to be in the XER
    for name in REQUIRED_TABLES:
        if name not in tables:
            errors.append(f"Missing Required Table {name}")

    # Check for required table pairs
    for t1, t2 in REQUIRED_TABLE_PAIRS.items():
        if t1 in tables and t2 not in tables:
            errors.append(f"Missing Table {t2} Required for Table {t1}")

    # check for tasks assigned to an invalid calendar (not included in CALENDAR TABLE)
    clndr_ids = [c["clndr_id"] for c in tables.get("CALENDAR", [])]
    tasks_with_invalid_calendar = [
        task for task in tables.get("TASK", []) if not task["clndr_id"] in clndr_ids
    ]
    if tasks_with_invalid_calendar:
        invalid_cal_count = len(
            set([t["clndr_id"] for t in tasks_with_invalid_calendar])
        )
        errors.append(
            f"XER is Missing {invalid_cal_count} Calendars Assigned to {len(tasks_with_invalid_calendar)} Tasks"
        )

    return errors
