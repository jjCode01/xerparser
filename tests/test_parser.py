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

from xerparser.src.xer import CALENDAR, PROJECT, Xer

DATE_FORMAT = "%Y-%m-%d %M:%S"  # format datetime objects to strings
PLANNED_DAYS = 14  # planned days ahead of data date for planned_progress testing
MAX_TEST_FILES = 250  # maximum number of files to test


def process_xer(file: Path):
    with open(file, encoding=Xer.CODEC, errors="ignore") as f:
        file_contents = f.read()

    xer = Xer(file_contents)
    xer_data = {
        project.short_name: process_project(project)
        for project in xer.projects.values()
    }

    return {
        "file": str(file.absolute()),
        "version": xer.export_info.version,
        "export_date": xer.export_info.date.strftime(DATE_FORMAT),
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
        "relationship_count": len(project.relationships),
        "remaining_cost": project.remaining_cost,
        "remaining_duration": project.remaining_duration,
        "task_count": len(project.tasks),
        "task_percent": project.task_percent,
        "this_period_cost": project.this_period_cost,
        "wbs_count": len(project.wbs_nodes),
    }


def process_planned_progress(progress: dict) -> dict[str, int]:
    prog_counts = {date: len(tasks) for date, tasks in progress.items()}
    return prog_counts


def process_calendar(calendar: CALENDAR):
    return {
        "name": calendar.name,
        "type": calendar.type,
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
                    "Could not find the directory in the config.py file."
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
            data for data in self.test_data if Path.is_file(Path(data["file"]))
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
            f"Running tests on {len(self.valid_data)} of {len(self.test_data)} .xer files."
        )

        for file in tqdm(self.valid_data):
            with open(file["file"], encoding=Xer.CODEC, errors="ignore") as f:
                file_contents = f.read()

            xer = Xer(file_contents)

            for project in xer.projects.values():
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
                self.assertEqual(
                    process_planned_progress(
                        project.planned_progress(
                            project.data_date + relativedelta(days=PLANNED_DAYS)
                        )
                    ),
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
                    f"{project.short_name} Project Task Percent Completew",
                )
                for calendar in project.calendars:
                    self.assertEqual(
                        [day for day, work in calendar.work_week.items() if work],
                        file[project.short_name]["calendars"][calendar.uid]["workdays"],
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


if __name__ == "__main__":
    print("Running tests....")
    unittest.main()
