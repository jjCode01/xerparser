# xerparser
# project.py

from collections import Counter
from datetime import datetime
from functools import cached_property
from statistics import mean
from typing import Any

from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.pcattype import PCATTYPE
from xerparser.schemas.pcatval import PCATVAL
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.schedoptions import SCHEDOPTIONS
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.taskrsrc import TASKRSRC
from xerparser.schemas.udftype import UDFTYPE
from xerparser.scripts.decorators import rounded
from xerparser.src.validators import date_format, optional_date, optional_str


class PROJECT:
    """
    A class representing a schedule.
    """

    _wbs_root: PROJWBS

    def __init__(
        self,
        sched_options: SCHEDOPTIONS,
        default_calendar: CALENDAR | None = None,
        **data: str,
    ) -> None:
        self.options: SCHEDOPTIONS = sched_options

        # table fields from .xer file
        self.uid: str = data["proj_id"]
        """Unique Table ID"""
        self.add_date: datetime = datetime.strptime(data["add_date"], date_format)
        """Date Project was Created"""
        self.default_calendar: CALENDAR | None = default_calendar
        """Default Calendar Assigned to Project"""
        self.data_date: datetime = datetime.strptime(
            data["last_recalc_date"], date_format
        )
        """Date Project is Updated To"""
        self.export_flag: bool = data["export_flag"] == "Y"
        """Project Export Flag"""
        self.finish_date: datetime = datetime.strptime(
            data["scd_end_date"], date_format
        )
        """Projected Completion Date"""
        self.last_fin_dates_id: str | None = optional_str(data["last_fin_dates_id"])
        """Last Stored Financial Period"""
        self.last_schedule_date: datetime | None = optional_date(
            data.get("last_schedule_date", "")
        )
        """Last Date Schedule was Calculated"""
        self.must_finish_date: datetime | None = optional_date(data["plan_end_date"])
        """Must Finish by Date Assigned to Project"""
        self.plan_start_date: datetime = datetime.strptime(
            data["plan_start_date"], date_format
        )
        """Planned Start Date Assigned to Project"""
        self.short_name: str = data["proj_short_name"]
        """Project Code"""

        # manually set from other tables
        self.activity_codes: list[ACTVTYPE] = []
        """Project Level Activity Codes"""
        self.calendars: list[CALENDAR] = []
        """Project Calendars"""
        self.project_codes: dict[PCATTYPE, PCATVAL] = {}
        """Project Codes Assigned to Project"""
        self.tasks: list[TASK] = []
        """Project Activities"""
        self.relationships: list[TASKPRED] = []
        """Project Relationships"""
        self.resources: list[TASKRSRC] = []
        """Activity Resources"""
        self.wbs_nodes: list[PROJWBS] = []
        """Project Work Breakdown Structure"""
        # self.wbs_root: PROJWBS | None = None
        self.user_defined_fields: dict[UDFTYPE, Any] = {}

    def __str__(self) -> str:
        return f"{self.short_name} - {self.name}"

    def __getitem__(self, obj: Any):
        if isinstance(obj, TASK):
            return self.tasks_by_code.get(obj.task_code)

        if isinstance(obj, TASKPRED):
            return self.relationships_by_hash.get(hash(obj))

        if isinstance(obj, PROJWBS):
            return self.wbs_by_path.get(obj.full_code)

    @cached_property
    @rounded()
    def actual_cost(self) -> float:
        """Sum of task resource actual costs"""
        return sum(res.act_total_cost for res in self.resources)

    @property
    def actual_duration(self) -> int:
        """Project actual duration in calendar days from start date to data date"""
        return max((0, (self.data_date - self.actual_start).days))

    @cached_property
    def actual_start(self) -> datetime:
        """Earliest task start date"""
        if not self.tasks:
            return self.plan_start_date
        return min((task.start for task in self.tasks))

    @cached_property
    @rounded()
    def budgeted_cost(self) -> float:
        """Sum of task resource budgeted costs"""
        return sum(res.target_cost for res in self.resources)

    @property
    @rounded(ndigits=4)
    def duration_percent(self) -> float:
        """Project duration percent complete"""
        if self.original_duration == 0:
            return 0.0

        if self.data_date >= self.finish_date:
            return 1.0

        return 1 - self.remaining_duration / self.original_duration

    @cached_property
    def finish_constraints(self) -> list[tuple[TASK, str]]:
        """List of all Tasks with Finish on or Before constraints"""
        return sorted(
            [
                (task, cnst)
                for task in self.tasks
                for cnst in ("prime", "second")
                if task.constraints[cnst]["type"] is TASK.ConstraintType.CS_MEOB
            ],
            key=lambda t: t[0].finish,
        )

    @cached_property
    def late_start(self) -> datetime:
        """Earliest task late start date"""
        if not self.tasks:
            return self.plan_start_date
        return min(
            (task.late_start_date for task in self.tasks if task.late_start_date)
        )

    @property
    def name(self) -> str:
        """Project Name"""
        if not self.wbs_root:
            return ""
        return self.wbs_root.name

    @property
    def original_duration(self) -> int:
        """
        Project overall duration in calendar days
        from actual start date to finish date
        """
        return (self.finish_date - self.actual_start).days

    @cached_property
    def relationships_by_hash(self) -> dict[int, TASKPRED]:
        return {hash(rel): rel for rel in self.relationships}

    @cached_property
    @rounded()
    def remaining_cost(self) -> float:
        """Sum of task resource remaining costs"""
        return sum(res.remain_cost for res in self.resources)

    @property
    def remaining_duration(self) -> int:
        """Project remaining duration in calendar days from data date to finish date"""
        return max((0, (self.finish_date - self.data_date).days))

    @cached_property
    @rounded(ndigits=4)
    def task_percent(self) -> float:
        """
        Project percent complete based on task updates.
        Calculated using the median of the following 2 ratios:

        * Ratio between Actual Dates and Activity Count.
        `(Actual Start Count + Actual Finish Count) ÷ (Activity Count * 2)`
        * Ratio between Sum of Task Remaining Durations and Task Original Durations.
        `1 - (sum of task remaining duration ÷ sum of task original duration)`
        """
        if not self.tasks:
            return 0.0

        orig_dur_sum = sum(
            task.original_duration
            for task in self.tasks
            if not any([task.type.is_loe, task.type.is_wbs])
        )
        rem_dur_sum = sum(
            task.remaining_duration
            for task in self.tasks
            if not any([task.type.is_loe, task.type.is_wbs])
        )
        task_dur_percent = 1 - rem_dur_sum / orig_dur_sum if orig_dur_sum else 0.0

        status_cnt = Counter([t.status for t in self.tasks])
        status_percent = (
            status_cnt[TASK.TaskStatus.TK_Active] / 2
            + status_cnt[TASK.TaskStatus.TK_Complete]
        ) / len(self.tasks)

        return mean([task_dur_percent, status_percent])

    @cached_property
    def tasks_by_code(self) -> dict[str, TASK]:
        """
        Returns a dictionary of the Activities using the
        Activity ID as the key and the TASK object as the value.
        """
        return {task.task_code: task for task in self.tasks}

    @cached_property
    @rounded()
    def this_period_cost(self) -> float:
        """Sum of task resource this period costs"""
        return sum(res.act_this_per_cost for res in self.resources)

    @cached_property
    def wbs_by_path(self) -> dict[str, PROJWBS]:
        return {node.full_code: node for node in self.wbs_nodes}

    @property
    def wbs_root(self) -> PROJWBS:
        if not self._wbs_root:
            raise UnboundLocalError("WBS Root is not assigned")

        return self._wbs_root

    @wbs_root.setter
    def wbs_root(self, value: PROJWBS) -> None:
        if not isinstance(value, PROJWBS):
            raise TypeError(f"wbs_root must be type `PROJWBS`; got {type(value)}")

        if value.code != self.short_name:
            raise ValueError(
                f"WBS Code ({value.code}) does not match project ({self.short_name})"
            )

        self._wbs_root = value

    def planned_progress(self, before_date: datetime) -> dict[str, list[TASK]]:
        """All planned progress through a given date.

        Args:
            before_date (datetime): End date for planned progress

        Returns:
            dict[str, list[TASK]]: Early and late planned progress during time frame
        """
        progress = {"start": [], "finish": [], "late_start": [], "late_finish": []}

        if before_date < self.data_date:
            return progress

        for task in self.tasks:
            if task.status.is_completed:
                continue

            if task.status.is_not_started:
                if task.start < before_date:
                    progress["start"].append(task)

                if task.late_start_date and task.late_start_date < before_date:
                    progress["late_start"].append(task)

            if task.finish < before_date:
                progress["finish"].append(task)

            if task.late_end_date and task.late_end_date < before_date:
                progress["late_finish"].append(task)

        return progress
