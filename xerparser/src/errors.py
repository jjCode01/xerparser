REQUIRED_TABLES = {"CALENDAR", "PROJECT", "PROJWBS", "TASK", "TASKPRED"}

REQUIRED_TABLE_PAIRS = {
    ("TASKFIN", "FINDATES"),
    ("TRSRCFIN", "FINDATES"),
    ("TASKRSRC", "RSRC"),
    ("TASKMEMO", "MEMOTYPE"),
    ("ACTVCODE", "ACTVTYPE"),
    ("TASKACTV", "ACTVCODE"),
}


def find_xer_errors(tables: dict) -> list[str]:
    """
    Find issues with the xer file, including
    - Missing tables
    - Non-existent calendars assigned to activities
    """
    # This list of required tables may be subjective
    # TODO: Add ability to pass in your own list of required tables.

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
    clndr_ids = [c["clndr_id"] for c in tables.get("CALENDAR", [])]
    export_projects = [
        p["proj_id"] for p in tables.get("PROJECT", []) if p["export_flag"] == "Y"
    ]
    tasks_with_invalid_calendar = [
        task
        for task in tables.get("TASK", [])
        if not task["clndr_id"] in clndr_ids and task["proj_id"] in export_projects
    ]
    if tasks_with_invalid_calendar:
        invalid_cal_count = len(
            set([t["clndr_id"] for t in tasks_with_invalid_calendar])
        )
        errors.append(
            f"XER is Missing {invalid_cal_count} Calendars Assigned to {len(tasks_with_invalid_calendar)} Tasks"
        )

    return errors
