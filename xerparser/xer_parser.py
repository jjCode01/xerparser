# xerparser
# xer_parser.py

from datetime import datetime
from typing import Iterator
from xerparser.schemas import *


__all__ = (
    "xer_to_dict",
    "Xer",
)

CODEC = "cp1252"


class Xer:
    def __init__(self, file: bytes | str) -> None:
        _tables = _split_to_tables(_read_file(file))

        self.version: str = _tables["ERMHDR"][0]
        self.export_date = datetime.strptime(_tables["ERMHDR"][1], "%Y-%m-%d")

        self.projects: dict[str, PROJECT] = {
            proj["proj_id"]: PROJECT(**proj)
            for proj in self._parse_table_rows(_tables.get("PROJECT"))
            if proj["export_flag"] == "Y"
        }

        self.accounts: dict[str, ACCOUNT] = {
            acct["acct_id"]: ACCOUNT(**acct)
            for acct in self._parse_table_rows(_tables.get("ACCOUNT"))
        }

        self.notebooks: dict[str, MEMOTYPE] = {
            topic["memo_type_id"]: MEMOTYPE(**topic)
            for topic in self._parse_table_rows(_tables.get("MEMOTYPE"))
        }

        self.resources: dict[str, RSRC] = {
            rsrc["rsrc_id"]: RSRC(**rsrc)
            for rsrc in self._parse_table_rows(_tables.get("RSRC"))
        }

        self.calendars: dict[str, CALENDAR] = {
            cal["clndr_id"]: CALENDAR(**cal)
            for cal in self._parse_table_rows(_tables.get("CALENDAR"))
        }

        self.wbs: dict[str, PROJWBS] = {
            wbs["wbs_id"]: PROJWBS(**wbs)
            for wbs in self._parse_table_rows(_tables.get("PROJWBS"))
            if wbs["proj_id"] in self.projects
        }

        for wbs in self.wbs.values():
            if not wbs.is_project_node:
                wbs.parent = self.wbs[wbs.parent_wbs_id]
            else:
                self.projects[wbs.proj_id].name = wbs.wbs_name

        self.tasks: dict[str, TASK] = {
            task.task_id: task for task in self._iter_tasks(_tables.get("TASK"))
        }

        self.task_notes: dict[tuple, TASKMEMO] = {
            (note.task.task_code, note.topic): note
            for note in self._iter_memos(_tables.get("TASKMEMO"))
        }

        self.relationships: dict[tuple, TASKPRED] = {
            (rel.predecessor.task_code, rel.successor.task_code, rel.link): rel
            for rel in self._iter_relationships(_tables.get("TASKPRED"))
        }

        self.task_resources: dict[tuple, TASKRSRC] = {
            res.taskrsrc_id: res
            for res in self._iter_resources(_tables.get("TASKRSRC"))
        }

    def _iter_tasks(self, table: list) -> Iterator[TASK]:
        for task in self._parse_table_rows(table):
            if task["proj_id"] in self.projects:
                calendar = self.calendars[task["clndr_id"]]
                calendar.assignments += 1
                wbs = self.wbs[task["wbs_id"]]
                wbs.assignments += 1
                yield TASK(calendar=calendar, wbs=wbs, **task)

    def _iter_memos(self, table: list) -> Iterator[TASKMEMO]:
        for memo in self._parse_table_rows(table):
            if memo["proj_id"] in self.projects:
                task = self.tasks[memo["task_id"]]
                topic = self.notebooks[memo["memo_type_id"]].memo_type
                yield TASKMEMO(task=task, topic=topic, **memo)

    def _iter_relationships(self, table: list) -> Iterator[TASKPRED]:
        for rel in self._parse_table_rows(table):
            if rel["proj_id"] in self.projects and rel["pred_proj_id"] in self.projects:
                pred = self.tasks[rel["pred_task_id"]]
                succ = self.tasks[rel["task_id"]]
                yield TASKPRED(predecessor=pred, successor=succ, **rel)

    def _iter_resources(self, table: list) -> Iterator[TASKRSRC]:
        for res in self._parse_table_rows(table):
            if res["proj_id"] in self.projects:
                task = self.tasks[res["task_id"]]
                rsrc = self.resources.get(res["rsrc_id"])
                account = self.accounts.get(res["acct_id"])
                yield TASKRSRC(task=task, resource=rsrc, account=account, **res)

    def _parse_table_rows(self, table: list[str] | None):
        if table:
            cols = table[0].split("\t")[1:]  # First line is the column labels
            for row in table[1:]:
                if row and not row.startswith("%E"):
                    values = row.split("\t")[1:]
                    yield {
                        key.strip(): _empty_str_to_none(value)
                        for key, value in tuple(zip(cols, values))
                    }


def xer_to_dict(file: bytes | str) -> dict:
    """Reads a P6 .xer file and converts it into a Python dictionary object.
    Args:
        file (bytes | str): .xer file exported from P6.
    Returns:
        dict: Dictionary of the xer information and data tables
    """
    xer_data = {}
    table_list = _split_to_tables(_read_file(file))

    # The first row in the xer file includes information about the file
    version, export_date = table_list.pop(0).strip().split("\t")[1:3]
    xer_data["version"] = version
    xer_data["export_date"] = datetime.strptime(export_date, "%Y-%m-%d")
    xer_data["tables"] = {
        name: rows for table in table_list for name, rows in _parse_table(table).items()
    }
    xer_data["errors"] = _find_xer_errors(xer_data["tables"])

    return xer_data


def _read_file(file) -> list[str]:
    """
    Read file and verify it is a valid XER. Parse file into a list of tables.
    """
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
        return file_contents


def _read_file_path(file) -> list[str]:
    with open(file, encoding=CODEC, errors="ignore") as f:
        file_as_str = f.read()
    return file_as_str


def _read_file_bytes(file: bytes) -> list[str]:
    file_as_str = file.decode(CODEC, errors="ignore")
    return file_as_str


def _split_to_tables(file_contents: str) -> dict[str, str]:
    if not file_contents.startswith("ERMHDR"):
        raise ValueError(f"ValueError: invalid XER file")

    tables = file_contents.split("%T\t")

    return {
        name: data for table in tables for name, data in _parse_tbl_name(table).items()
    }


def _parse_tbl_name(table: str) -> dict:
    if table.startswith("ERMHDR"):
        values = table.strip().split("\t")
        name = values.pop(0).strip()
        return {name: values}

    lines = table.split("\n")
    name = lines[0].strip()
    data = lines[1:]
    return {name: data}


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines = table.split("\n")
    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).split("\t")[1:]  # Second line is the column labels

    data = [
        _eval_row(name, _row_to_dict(cols, row))
        for row in lines
        if row and not row.startswith("%E")
    ]

    return {name: data}


def _eval_row(name: str, row):
    if name in TABLE_MAP:
        obj = TABLE_MAP[name][0]
        return obj(**row)

    return row


def _row_to_dict(columns: list[str], row: str) -> dict:
    """Convert row of values to dictionary objects"""
    values = row.split("\t")[1:]
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
        for proj in xer.projects.values():
            print(
                proj.proj_short_name,
                proj.name,
                f"\n\tData Date: {proj.last_recalc_date: %d-%b-%Y}",
                f"\n\tEnd Date: {proj.scd_end_date: %d-%b-%Y}",
                f"\n\tTasks: {sum(task.proj_id == proj.proj_id for task in xer.tasks.values()):,}",
                f"\n\tRelationships: {sum((rel.proj_id == proj.proj_id for rel in xer.relationships.values())):,}",
            )
            print("------------------------------\n")
