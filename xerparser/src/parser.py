# xerparser
# xer.py

from datetime import datetime

CODEC = "cp1252"


def xer_to_dict(file: bytes | str) -> dict:
    """Reads a P6 .xer file and converts it into a Python dictionary object.
    Args:
        file (bytes | str): .xer file exported from P6.
    Returns:
        dict: Dictionary of the xer information and data tables
    """
    xer_data = {}
    table_list = _split_tables(_read_file(file))

    # The first row in the xer file includes information about the file
    xer_data["ERMHDR"] = table_list.pop(0).strip().split("\t")[1:]
    xer_data["tables"] = {
        name: rows for table in table_list for name, rows in _parse_table(table).items()
    }
    xer_data["errors"] = _find_xer_errors(xer_data["tables"])

    return xer_data


<<<<<<< HEAD:xerparser/xer_parser.py
def _parse_file_to_list_of_tables(file) -> list[str]:
=======
def _read_file(file) -> list[str]:
>>>>>>> development:xerparser/src/parser.py
    """
    Read file and verify it is a valid XER. Parse file into a list of tables.
    """
    file_contents = ""

<<<<<<< HEAD:xerparser/xer_parser.py
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
=======
    try:
        file_contents = _read_file_path(file)
    except:
        pass
    else:
        return file_contents

    try:
        file_contents = _read_file_bytes(file)
    except:
        pass
    else:
        return file_contents

    try:
        file_contents = file.read().decode(CODEC, errors="ignore")
    except:
        raise ValueError("Cannot Read File")
    else:
        return file_contents


def _read_file_path(file) -> list[str]:
    with open(file, encoding=CODEC, errors="ignore") as f:
        file_as_str = f.read()
    return file_as_str


def _read_file_bytes(file: bytes) -> list[str]:
    file_as_str = file.decode(CODEC, errors="ignore")
    return file_as_str


def _split_tables(file_contents: str) -> dict[str, str]:
    if not file_contents.startswith("ERMHDR"):
        raise ValueError(f"ValueError: invalid XER file")

    return file_contents.split("%T\t")
>>>>>>> development:xerparser/src/parser.py


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines: list[str] = table.split("\n")
    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).strip().split("\t")[1:]  # Second line is the column labels

    data = [
        dict(zip(cols, row.strip().split("\t")[1:]))
        for row in lines
        if row.startswith("%R")
    ]

    return {name: data}


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
