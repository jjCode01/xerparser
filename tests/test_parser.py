"""
Unittests for xerparser.

1. Setup the config.py file - follow instructions in config_template.py

2. Run the tests before making any code changes.
    - On the first run, you will be prompted to create a `xer_data.json` file - select y.
    - This will run through each .xer file in the specified directory, create a Xer object,
    and outputs the values of various attributes, properties, and methods to a json file.

3. The subsequent tests will run through each .xer file in the specified directory, create a Xer object,
and compare it's attribute/property/method return values against the values stored in the json file.
    - The test will fail if any values differ between the Xer object and the json file.
    - The test will also fail if any Exceptions (other than CorruptXerFile) are raised during initialzation of the Xer object.
"""

import json
import os
import sys
import unittest
from multiprocessing import Pool
from pathlib import Path
from typing import Any

from dateutil.relativedelta import relativedelta
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tests.config as config
from xerparser.src.errors import CorruptXerFile
from xerparser.src.xer import CALENDAR, PROJECT, Xer

DATE_FORMAT = "%Y-%m-%d %M:%S"  # format datetime objects to strings
PLANNED_DAYS = 14  # planned days ahead of data date for planned_progress testing
MAX_TEST_FILES = 250  # maximum number of files to test


def process_xer(file: Path) -> dict | None:
    try:
        xer = Xer.reader(file)
    except CorruptXerFile as e:
        return {"file": str(file.absolute()), "errors": e.errors}
    except KeyError as e:
        return {"file": str(file.absolute()), "errors": str(e)}

    xer_data = {
        project.short_name: process_project(project)
        for project in xer.projects.values()
    }

    return {
        "file": str(file.absolute()),
        "version": xer.export_info.version,
        "export_date": xer.export_info.date.strftime(DATE_FORMAT),
        "accounts": len(xer.accounts),
        "udf_types": [
            {"label": udf.label, "table": udf.table, "type": udf.type.value}
            for udf in xer.udf_types.values()
        ],
        **xer_data,
    }


def process_project(project: PROJECT) -> dict[str, Any]:
    return {
        "name": project.name,
        "activity_codes": [code.name for code in project.activity_codes],
        "actual_cost": project.actual_cost,
        "actual_start_date": project.actual_start.strftime(DATE_FORMAT),
        "budget_cost": project.budgeted_cost,
        "calendars": {cal.uid: process_calendar(cal) for cal in project.calendars},
        "duration_percent": project.duration_percent,
        "original_duration": project.original_duration,
        "planned_progress": process_planned_progress(
            project.planned_progress(
                project.data_date + relativedelta(days=PLANNED_DAYS)
            )
        ),
        "project_codes": {
            code.name: val.code for code, val in project.project_codes.items()
        },
        "relationship_count": len(project.relationships),
        "remaining_cost": project.remaining_cost,
        "remaining_duration": project.remaining_duration,
        "task_activity_code_count": sum(
            len(task.activity_codes) for task in project.tasks
        ),
        "task_count": len(project.tasks),
        "task_memo_count": sum(len(task.memos) for task in project.tasks),
        "task_period_count": sum(len(task.periods) for task in project.tasks),
        "task_resource_count": sum(len(task.resources) for task in project.tasks),
        "task_percent": project.task_percent,
        "task_udf_count": sum(len(task.user_defined_fields) for task in project.tasks),
        "this_period_cost": project.this_period_cost,
        "wbs_count": len(project.wbs_nodes),
    }


def process_planned_progress(progress: dict) -> dict[str, int]:
    prog_counts = {date: len(tasks) for date, tasks in progress.items()}
    return prog_counts


def process_calendar(calendar: CALENDAR):
    return {
        "name": calendar.name,
        "type": calendar.type.value,
        "workdays": [weekday for weekday, day in calendar.work_week.items() if day],
        "workweek_hours": sum([day.hours for day in calendar.work_week.values()]),
        "holiday_count": len(calendar.holidays),
        "work_exception_count": len(calendar.work_exceptions),
    }


def create_test_data(file_directory: Path) -> None:
    files = [file for file in file_directory.glob("**/*.xer")]

    if not files:
        raise FileNotFoundError(f"No .xer files found in {file_directory.absolute()}")

    print(f"Found {len(files)} xer files... Max files to test is {MAX_TEST_FILES}")

    if len(files) > MAX_TEST_FILES:
        files = files[:MAX_TEST_FILES]

    with Pool() as p:
        data_list = list(
            tqdm(
                p.imap(process_xer, files),
                total=len(files),
            )
        )

    json_data = json.dumps(data_list, indent=4)
    file_path = Path("./tests/fixtures")
    if not Path.exists(file_path):
        Path.mkdir(file_path)

    with open("./tests/fixtures/xer_data.json", "w") as outfile:
        outfile.write(json_data)


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        xer_data_file = Path(r"./tests/fixtures/xer_data.json")
        if not Path.is_file(xer_data_file):
            if not Path.exists(Path(config.directory)):
                raise FileNotFoundError(
                    f"Could not find the directory in the config.py file {config.directory}"
                )

            create_data = input(
                "Test data file [xer_data.json] does not exist, would you like to attempt to create it? (y/n)  "
            )
            if create_data.lower() == "y":
                print("Creating test data....")
                create_test_data(Path(config.directory))
            else:
                raise FileNotFoundError("Could not find xer_data.json")

        with open(xer_data_file) as f:
            self.test_data: dict = json.load(f)

        self.valid_data = [
            data for data in self.test_data if data and Path.is_file(Path(data["file"]))
        ]

        if not self.valid_data:
            re_create_data = input(
                "Test data file [xer_data.json] does not reference valid .xer files, would you like to attempt to re-create it? (y/n)  "
            )

            if re_create_data.lower() == "y":
                print("Re-creating test data....")
                create_test_data(Path(config.directory))

    def test_create_xer(self):
        """Tests creation of Xer objects"""

        print(
            f"Running xer parser tests on {len(self.valid_data)} of {len(self.test_data)} .xer files."
        )

        for file in tqdm(self.valid_data):
            try:
                xer = Xer.reader(file["file"])
            except CorruptXerFile as e:
                self.assertEqual(e.errors, file["errors"])
            except KeyError as e:
                self.assertEqual(str(e), file["errors"])
            else:
                self.assertEqual(len(xer.accounts), file["accounts"])

                self.assertEqual(
                    [
                        {"label": udf.label, "table": udf.table, "type": udf.type.value}
                        for udf in xer.udf_types.values()
                    ],
                    file["udf_types"],
                )

                for project in xer.projects.values():
                    self.assertEqual(
                        project.name,
                        file[project.short_name]["name"],
                        f"{project.short_name} Name",
                    )
                    self.assertEqual(
                        project.budgeted_cost,
                        file[project.short_name]["budget_cost"],
                        f"{project.short_name} Budgeted Cost",
                    )
                    self.assertEqual(
                        project.actual_cost,
                        file[project.short_name]["actual_cost"],
                        f"{project.short_name} Actual Cost",
                    )
                    self.assertEqual(
                        project.this_period_cost,
                        file[project.short_name]["this_period_cost"],
                        f"{project.short_name} This Period Cost",
                    )
                    self.assertEqual(
                        project.remaining_cost,
                        file[project.short_name]["remaining_cost"],
                        f"{project.short_name} Remaining Cost",
                    )
                    self.assertEqual(
                        [code.name for code in project.activity_codes],
                        file[project.short_name]["activity_codes"],
                        f"{project.short_name} Activity Codes",
                    )
                    self.assertEqual(
                        {
                            code.name: val.code
                            for code, val in project.project_codes.items()
                        },
                        file[project.short_name]["project_codes"],
                        f"{project.short_name} Project Codes",
                    )
                    self.assertEqual(
                        project.actual_start.strftime(DATE_FORMAT),
                        file[project.short_name]["actual_start_date"],
                        f"{project.short_name} Project Acutal Start",
                    )
                    self.assertEqual(
                        project.duration_percent,
                        file[project.short_name]["duration_percent"],
                        f"{project.short_name} Project Duration Percent",
                    )
                    self.assertEqual(
                        project.original_duration,
                        file[project.short_name]["original_duration"],
                        f"{project.short_name} Project Duration Percent",
                    )
                    planned_progress = project.planned_progress(
                        project.data_date + relativedelta(days=PLANNED_DAYS)
                    )
                    self.assertEqual(
                        process_planned_progress(planned_progress),
                        file[project.short_name]["planned_progress"],
                        f"{project.short_name} Project Planned Progress Counts",
                    )
                    self.assertEqual(
                        project.remaining_duration,
                        file[project.short_name]["remaining_duration"],
                        f"{project.short_name} Project Remaining Duration",
                    )
                    self.assertEqual(
                        project.task_percent,
                        file[project.short_name]["task_percent"],
                        f"{project.short_name} Project Task Percent Complete",
                    )
                    self.assertEqual(
                        sum(len(task.memos) for task in project.tasks),
                        file[project.short_name]["task_memo_count"],
                        f"{project.short_name} Project Task Memo Count",
                    )
                    self.assertEqual(
                        sum(len(task.periods) for task in project.tasks),
                        file[project.short_name]["task_period_count"],
                        f"{project.short_name} Project Task Period Count",
                    )
                    self.assertEqual(
                        sum(len(task.resources) for task in project.tasks),
                        file[project.short_name]["task_resource_count"],
                        f"{project.short_name} Project Task Resource Count",
                    )
                    self.assertEqual(
                        sum(len(task.activity_codes) for task in project.tasks),
                        file[project.short_name]["task_activity_code_count"],
                        f"{project.short_name} Project Task Activity Code Count",
                    )
                    self.assertEqual(
                        sum(len(task.user_defined_fields) for task in project.tasks),
                        file[project.short_name]["task_udf_count"],
                        f"{project.short_name} Project Task UDF Count",
                    )
                    self.assertEqual(
                        sum(len(task.predecessors) for task in project.tasks),
                        file[project.short_name]["relationship_count"],
                        f"{project.short_name} Project Task Predecessor Count",
                    )
                    self.assertEqual(
                        sum(len(task.successors) for task in project.tasks),
                        file[project.short_name]["relationship_count"],
                        f"{project.short_name} Project Task Successor Count",
                    )
                    for calendar in project.calendars:
                        self.assertEqual(
                            [day for day, work in calendar.work_week.items() if work],
                            file[project.short_name]["calendars"][calendar.uid][
                                "workdays"
                            ],
                            f"{project.short_name} - Calendar {calendar.uid} work week",
                        )
                        self.assertEqual(
                            sum((day.hours for day in calendar.work_week.values())),
                            file[project.short_name]["calendars"][calendar.uid][
                                "workweek_hours"
                            ],
                            f"{project.short_name} - Calendar {calendar.uid} work week hoursr",
                        )
                        self.assertEqual(
                            len(calendar.holidays),
                            file[project.short_name]["calendars"][calendar.uid][
                                "holiday_count"
                            ],
                            f"{project.short_name} - Calendar {calendar.uid} holiday count",
                        )
                        self.assertEqual(
                            len(calendar.work_exceptions),
                            file[project.short_name]["calendars"][calendar.uid][
                                "work_exception_count"
                            ],
                            f"{project.short_name} - Calendar {calendar.uid} exception count",
                        )

    def test_rem_hour_calc(self):
        """Tests calculation of task rem work hours"""

        print(
            f"Running calc remaining hours tests on {len(self.valid_data)} of {len(self.test_data)} .xer files."
        )

        for file in tqdm(self.valid_data):
            with open(file["file"], encoding=Xer.CODEC, errors="ignore") as f:
                file_contents = f.read()
            try:
                xer = Xer(file_contents)
            except CorruptXerFile:
                continue
            except KeyError:
                continue

            for project in xer.projects.values():
                for task in project.tasks:
                    if task.status.is_completed or not task.restart_date:
                        continue
                    if task.type.is_milestone:
                        continue
                    if not task.calendar:
                        continue

                    rem_hours = task.rem_hours_per_day()
                    self.assertEqual(
                        round(sum(day for day in rem_hours.values()), 2),
                        round(task.remain_drtn_hr_cnt, 2),
                        f"{project.short_name} - {project.name}\n{task}\nCalendar{task.calendar}\nStart: {task.restart_date}\nFinish: {task.reend_date}\nRem Hours: {task.remain_drtn_hr_cnt}\n{rem_hours}",
                    )


if __name__ == "__main__":
    print("Running tests....")
    unittest.main()
