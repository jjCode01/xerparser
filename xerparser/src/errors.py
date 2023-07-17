# xerparser
# errors.py


class CorruptXerFile(Exception):
    """Raised when xer contains missing data."""

    def __init__(self, errors: list[str], message="XER file is corrupt") -> None:
        self.errors = errors
        self.message = message

    def __str__(self) -> str:
        error_list = "\n".join(self.errors)
        return f"{self.message}\n{error_list}"


class InvalidParent(Exception):
    """Raised when Parent does not match parent id."""

    def __init__(self, parent_id: str, expected_id: str | None) -> None:
        self.message = f"Expcted parent with id {parent_id}, got {expected_id}"

    def __str__(self) -> str:
        return self.message


def find_xer_errors(tables: dict) -> list[str]:
    """
    Find issues with the xer file, including
    - Missing tables
    - Non-existent calendars assigned to activities
    """
    # This list of required tables may be subjective
    # TODO: Add ability to pass in your own list of required tables.

    REQUIRED_TABLES = {"CALENDAR", "PROJECT", "PROJWBS", "TASK", "TASKPRED"}
    REQUIRED_TABLE_PAIRS = {
        ("TASKFIN", "FINDATES"),
        ("TRSRCFIN", "FINDATES"),
        ("TASKRSRC", "RSRC"),
        ("TASKMEMO", "MEMOTYPE"),
        ("ACTVCODE", "ACTVTYPE"),
        ("TASKACTV", "ACTVCODE"),
        ("PCATVAL", "PCATTYPE"),
        ("PROJPCAT", "PCATVAL"),
        ("UDFVALUE", "UDFTYPE"),
    }

    errors = []

    # Check for minimum tables required to be in the XER
    for name in REQUIRED_TABLES:
        if name not in tables:
            errors.append(f"Missing Required Table {name}")

    # Check for required table pairs
    for t1, t2 in REQUIRED_TABLE_PAIRS:
        if t1 in tables and t2 not in tables:
            errors.append(f"Missing Table {t2} Required for Table {t1}")

    # check for tasks assigned to an invalid calendar (not included in CALENDAR TABLE)
    clndr_ids = {c["clndr_id"] for c in tables.get("CALENDAR", [])}
    export_projects = {
        p["proj_id"] for p in tables.get("PROJECT", []) if p["export_flag"] == "Y"
    }
    tasks_with_invalid_calendar = [
        task
        for task in tables.get("TASK", [])
        if task["clndr_id"] not in clndr_ids and task["proj_id"] in export_projects
    ]
    if tasks_with_invalid_calendar:
        invalid_cal_count = len({t["clndr_id"] for t in tasks_with_invalid_calendar})
        errors.append(
            f"XER is Missing {invalid_cal_count} Calendars Assigned to {len(tasks_with_invalid_calendar)} Tasks"
        )

    # check for missing resources (not included in RSRC TABLE)
    rsrc_ids = {r["rsrc_id"] for r in tables.get("RSRC", [])}
    task_rsrc_with_invalid_rsrc = [
        res
        for res in tables.get("TASKRSRC", [])
        if res["rsrc_id"] not in rsrc_ids and res["proj_id"] in export_projects
    ]
    if task_rsrc_with_invalid_rsrc:
        invalid_rsrc_count = len({r["rsrc_id"] for r in task_rsrc_with_invalid_rsrc})
        errors.append(
            f"XER is Missing {invalid_rsrc_count} Resources Assigned to {len(task_rsrc_with_invalid_rsrc)} Task Resources."
        )
    return errors
