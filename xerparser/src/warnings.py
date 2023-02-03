# xerparser
# warnings.py

from datetime import datetime
from enum import Enum
from itertools import groupby
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.project import PROJECT
from xerparser.schemas.task import TASK, LinkToTask
from xerparser.schemas.taskpred import TASKPRED

major_holidays_us = {
    "New Years Day": (1, 1),
    "Memorial Day": (5, 1, -1),  # Last Monday in May
    "Independence Day": (7, 4),
    "Labor Day": (9, 1, 0),  # First Monday in September
    "Thanksgiving": (11, 5, 3),  # Fourth Thursday in November
    # "Day after Thanksgiving"
    "Christmas": (12, 25),
}


class ScheduleWarnings:
    def __init__(
        self,
        project: PROJECT,
        long_duration_value: int = 20,
        long_lag_value: int = 10,
    ) -> None:

        if not isinstance(project, PROJECT):
            raise TypeError(
                f"project agrument must be <class 'PROJECT'>; got {type(project)}"
            )

        _validate_positive_integer(
            long_duration_value=long_duration_value, long_lag_value=long_lag_value
        )
        self.long_duration_value = long_duration_value
        self.long_lag_value = long_lag_value
        self.open_predecessors: list[TASK] = []  # DONE
        self.open_successors: list[TASK] = []  # DONE
        self.open_finishes: list[TASK] = []  # DONE
        self.open_starts: list[TASK] = []  # DONE

        self.long_durations: list[TASK] = []  # ***** NEEDS WORK******
        self.invalid_start: list[TASK] = []  # DONE
        self.invalid_finish: list[TASK] = []  # DONE
        self.no_progress: list[TASK] = []

        self.duplicate_logic: list[tuple[TASK, tuple[LinkToTask]]] = []  # DONE
        self.start_finish_links: list[TASKPRED] = []  # DONE
        self.negative_lags: list[TASKPRED] = []  # DONE
        self.long_lags: list[TASKPRED] = []  # DONE
        self.fs_with_lag: list[TASKPRED] = []  # Done
        self.lag_gt_duration: list[TASKPRED] = []  # DONE

        self.cost_variance: list[TASK] = []  # Done

        self.calendar_missing_holidays: dict[CALENDAR, list[datetime]] = {}

        dup_name_grp = groupby(
            sorted(project.tasks, key=lambda task: task.name), lambda task: task.name
        )
        self.duplicate_names: list[tuple[TASK]] = [
            tasks for _, grp in dup_name_grp if len(tasks := tuple(grp)) > 1
        ]
        self.duplicate_names_cnt: int = sum(len(grp) for grp in self.duplicate_names)

        for task in sorted(project.tasks):
            if not task.predecessors:
                self.open_predecessors.append(task)
            else:
                for pred in task.predecessors:
                    if pred.link in ("FS", "SS"):
                        break
                else:
                    self.open_starts.append(task)

            if not task.successors:
                self.open_successors.append(task)
            else:
                for succ in task.successors:
                    if succ.link in ("FS", "FF"):
                        break
                else:
                    self.open_finishes.append(task)

            if task.act_start_date and task.act_start_date >= project.data_date:
                self.invalid_start.append(task)

            if task.act_end_date and task.act_end_date >= project.data_date:
                self.invalid_finish.append(task)

            # TODO: Check if task is a submittal before adding to long durations
            if not task.type.is_loe and task.original_duration > long_duration_value:
                self.long_durations.append(task)

            if (
                task.status.is_in_progress
                and task.percent_complete == 0
                and task.remaining_duration == task.original_duration
            ):
                self.no_progress.append(task)

            if task.at_completion_cost != task.budgeted_cost:
                self.cost_variance.append(task)

            succ_grp = groupby(
                sorted(task.successors, key=lambda succ: succ.task),
                lambda succ: succ.task,
            )
            for _, grp in succ_grp:
                if len(succs := tuple(grp)) > 1:
                    if "FS" in [succ.link for succ in succs]:
                        self.duplicate_logic.append((task, succs))

        for relationship in sorted(project.relationships):
            if relationship.lag < 0:
                self.negative_lags.append(relationship)

            if relationship.lag >= long_lag_value:
                self.long_lags.append(relationship)

            if relationship.link == "SF":
                self.start_finish_links.append(relationship)

            if relationship.link == "FS" and relationship.lag > 0:
                self.fs_with_lag.append(relationship)

            if (
                relationship.link == "SS"
                and 0 < relationship.predecessor.duration <= relationship.lag
            ):
                self.lag_gt_duration.append(relationship)

            if (
                relationship.link == "FF"
                and 0 < relationship.successor.duration <= relationship.lag
            ):
                self.lag_gt_duration.append(relationship)


def _validate_positive_integer(**kwargs) -> None:
    for key, value in kwargs.items():
        if not isinstance(value, int):
            raise TypeError(f"{key} agrgument must be type 'int'; got {type(value)}")

        if value <= 0:
            raise ValueError(f"{key} argument must be a positive integer; got {value}")
