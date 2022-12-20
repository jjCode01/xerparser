# xerparser
# warnings.py

from datetime import datetime
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.project import PROJECT
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED


class ScheduleWarnings:
    def __init__(
        self, project: PROJECT, long_duration_value: int = 20, long_lag_value: int = 10
    ) -> None:

        if not isinstance(project, PROJECT):
            raise TypeError(
                f"project agrument must be <class 'PROJECT'>; got {type(project)}"
            )

        _validate_positive_integer(
            long_duration_value=long_duration_value, long_lag_value=long_lag_value
        )
        self.open_predecessors: list[TASK] = []
        self.open_successors: list[TASK] = []
        self.open_finishes: list[TASK] = []
        self.open_starts: list[TASK] = []

        self.long_durations: list[TASK] = []
        self.duplicate_names: dict[str, list[TASK]] = {}
        self.invalid_start: list[TASK] = []  # Actual Start >= Data Date
        self.invalid_finish: list[TASK] = []  # Actual Finish >= Data Date

        self.duplicate_logic: list[TASKPRED] = []
        self.start_finish_links: list[TASKPRED] = []
        self.negative_lags: list[TASKPRED] = []
        self.long_lags: list[TASKPRED] = []
        self.fs_with_lag: list[TASKPRED] = []
        self.lag_gt_duration: list[TASKPRED] = []

        self.cost_variance: list[TASK]  # At Completion Cost != Budgeted Cost

        self.calendar_missing_holidays: dict[CALENDAR, list[datetime]] = {}

        for task in project.tasks.values():
            if not task.has_predecessor:
                self.open_predecessors.append(task)

            if not task.has_successor:
                self.open_successors.append(task)

            if not task.has_finish_successor:
                self.open_finishes.append(task)

            if not task.has_start_predecessor:
                self.open_starts.append(task)


def _validate_positive_integer(**kwargs) -> None:
    for key, value in kwargs:
        if not isinstance(value, int):
            raise TypeError(f"{key} agrgument must be type 'int'; got {type(value)}")

        if value <= 0:
            raise ValueError(f"{key} argument must be a positive integer; got {value}")
