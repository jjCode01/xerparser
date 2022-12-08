# xerparser
# xer_parser.py

from datetime import datetime
from pydantic import BaseModel
from xerparser.schemas import *


__all__ = (
    "xer_to_dict",
    "Xer",
)

CODEC = "cp1252"


class Xer:
    def __init__(self, file: bytes | str) -> None:
        _xer_dict = xer_to_dict(file)
        self.version: str = _xer_dict["version"]
        self.export_date: datetime = _xer_dict["export_date"]
        self.tables = _xer_dict["tables"]

        # _tables: dict[str, dict] = _xer_dict["tables"]
        # self.project: list[PROJECT] = _tables.get("PROJECT", [])
        # self.projwbs: list[PROJWBS] = _tables.get("PROJWBS", [])
        # self.calendar: list[CALENDAR] = _tables.get("CALENDAR", [])
        # self.task: list[TASK] = _tables.get("TASK", [])
        # self.taskpred: list[TASKPRED] = _tables.get("TASKPRED", [])


def xer_to_dict(file: bytes | str) -> dict:
    """Reads a P6 .xer file and converts it into a Python dictionary object.
    Args:
        file (bytes | str): .xer file exported from P6.
    Returns:
        dict: Dictionary of the xer information and data tables
    """
    xer_data = {}
    table_list = _split_file_into_tables(file)

    # The first row in the xer file includes information about the file
    version, export_date = table_list.pop(0).strip().split("\t")[1:3]
    xer_data["version"] = version
    xer_data["export_date"] = datetime.strptime(export_date, "%Y-%m-%d")
    xer_data["tables"] = {
        name: rows for table in table_list for name, rows in _parse_table(table).items()
    }
    xer_data["errors"] = _find_xer_errors(xer_data["tables"])

    return xer_data


def _split_file_into_tables(file) -> list[str]:
    """
    Read file and verify it is a valid XER. Parse file into a list of tables.
    """

    # TODO: Add ability to read UploadFile from fastapi.
    file_contents = ""

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
        return _verify_file(file_contents)


def _read_file_path(file) -> list[str]:
    with open(file, encoding=CODEC, errors="ignore") as f:
        file_as_str = f.read()
    return _verify_file(file_as_str)


def _read_file_bytes(file: bytes) -> list[str]:
    file_as_str = file.decode(CODEC, errors="ignore")
    return _verify_file(file_as_str)


def _verify_file(file_contents: str) -> list[str]:
    if not file_contents.startswith("ERMHDR"):
        raise ValueError(f"ValueError: invalid XER file")

    return file_contents.split("%T\t")


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines = table.split("\n")
    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).split("\t")[1:]  # Second line is the column labels
    table = {
        name: [
            _eval_table_row(name, cols, line.split("\t")[1:])
            for line in lines
            if line and not line.startswith("%E")
        ]
    }
    return table


def _eval_table_row(name, col, row):
    # if name in TABLE_TO_CLASS:
    #     return TABLE_TO_CLASS[name](**_row_to_dict(col, row))

    try:
        return TableMap[name].value(**_row_to_dict(col, row))
    except KeyError:
        return _row_to_dict(col, row)

    # if name in TABLE_TO_CLASS:
    #     return TABLE_TO_CLASS[name](**_row_to_dict(col, row))

    # return _row_to_dict(col, row)


def _row_to_dict(columns: list[str, str], values: list) -> dict[str, str]:
    """Convert row of values to dictionary objects"""
    row = {
        key.strip(): _empty_str_to_none(val) for key, val in tuple(zip(columns, values))
    }
    return row


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
    clndr_ids = [c.clndr_id for c in tables.get("CALENDAR", [])]
    tasks_with_invalid_calendar = [
        task for task in tables.get("TASK", []) if not task.clndr_id in clndr_ids
    ]
    if tasks_with_invalid_calendar:
        invalid_cal_count = len(set([t.clndr_id for t in tasks_with_invalid_calendar]))
        errors.append(
            f"XER is Missing {invalid_cal_count} Calendars Assigned to {len(tasks_with_invalid_calendar)} Tasks"
        )

    return errors


if __name__ == "__main__":
    from pathlib import Path

    directory = "/home/jesse/xer_files/"
    # xer_directory = os.path.join(directory, "xer_files")
    files = Path(directory).glob("*.xer")

    for file in files:
        print(file)
        xer = Xer(file)
        print(xer.version, xer.export_date)
        for proj in xer.tables["PROJECT"]:
            print(
                proj.proj_short_name,
                f"Data Date: {proj.last_recalc_date: %d-%b-%Y}",
                f"End Date: {proj.scd_end_date: %d-%b-%Y}",
                f"Tasks: {sum((task.proj_id == proj.proj_id for task in xer.tables['TASK'])):,}",
                f"Relationships: {sum((rel.proj_id == proj.proj_id for rel in xer.tables['TASKPRED'])):,}",
            )
            print("------------------------------\n")
