# xerparser
# project.py

from collections import Counter
from datetime import datetime
from functools import cached_property
from pydantic import BaseModel, Field, validator
from statistics import mean
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED

field_can_be_none = ("last_fin_dates_id", "last_schedule_date", "must_finish_date")


class PROJECT(BaseModel):
    """
    A class representing a schedule.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [proj_id]
    actual_cost: float
        Actual Cost to Date
    add_date: datetime
        Date Added
    budgeted_cost: float
        Budgeted Cost
    data_date: datetime
        Schedule data date [last_recalc_date]
    export_flag: bool
        Project Export Flag
    finish_date: datetime
        Scheduled Finish [scd_end_date]
    last_fin_dates_id: str | None
        Last Financial Period
    last_schedule_date: datetime | None
        Date Last Scheduled
    must_finish_date: datetime | None
        Must Finish By [plan_end_date]
    name: str
        Project Name
    plan_start_date: datetime
        Planned Start
    remaining_cost: float
        Remaining Cost
    short_name: str
        Project ID [proj_short_name]
    this_period_cost: float
        Actual Cost this Period
    relationships: list[TASKPRED]
        List of Project Relationships
    tasks: list[TASK]
        List of Project Activities
    wbs: list[PROJWBS]
        List of Project WBS Nodes

    """

    # table fields from .xer file
    uid: str = Field(alias="proj_id")
    add_date: datetime
    data_date: datetime = Field(alias="last_recalc_date")
    export_flag: bool
    finish_date: datetime = Field(alias="scd_end_date")
    last_fin_dates_id: str | None
    last_schedule_date: datetime | None
    must_finish_date: datetime | None = Field(alias="plan_end_date")
    plan_start_date: datetime
    short_name: str = Field(alias="proj_short_name")

    # manually set from other tables
    activity_codes: list[ACTVTYPE] = []
    calendars: list[CALENDAR] = []
    name: str = ""
    tasks: list[TASK] = []
    relationships: list[TASKPRED] = []
    wbs_nodes: list[PROJWBS] = []

    @validator("export_flag", pre=True)
    def flag_to_bool(cls, value):
        return value == "Y"

    @validator(*field_can_be_none, pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @cached_property
    def actual_cost(self) -> float:
        """Sum of task resource actual costs"""
        return round(sum(task.actual_cost for task in self.tasks), 2)

    @cached_property
    def actual_start(self) -> datetime:
        """Earliest task start date"""
        if not self.tasks:
            return self.plan_start_date
        return min((task.start for task in self.tasks))

    @cached_property
    def budgeted_cost(self) -> float:
        """Sum of task resource budgeted costs"""
        return round(sum(task.budgeted_cost for task in self.tasks), 2)

    @property
    def duration_percent(self) -> float:
        """Project duration percent complete"""
        if self.original_duration == 0:
            return 0.0

        if self.data_date >= self.finish_date:
            return 1.0

        return round(1 - self.remaining_duration / self.original_duration, 4)

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

    @property
    def original_duration(self) -> int:
        "Project overall duration in calendar days from actual start date to finish date"
        return (self.finish_date - self.actual_start).days

    @cached_property
    def relationships_by_hash(self) -> dict[int, TASKPRED]:
        return {hash(rel): rel for rel in self.relationships}

    @cached_property
    def remaining_cost(self) -> float:
        """Sum of task resource remaining costs"""
        return round(sum(task.remaining_cost for task in self.tasks), 2)

    @property
    def remaining_duration(self) -> int:
        """Project remaining duration in calendar days from data date to finish date"""
        return max((0, (self.finish_date - self.data_date).days))

    @cached_property
    def task_percent(self) -> float:
        """Calculated Project percent complete based on task updates"""
        if not self.tasks:
            return 0.0

        orig_dur_sum = sum((task.original_duration for task in self.tasks))
        rem_dur_sum = sum((task.remaining_duration for task in self.tasks))
        task_dur_percent = 1 - rem_dur_sum / orig_dur_sum if orig_dur_sum else 0.0

        status_cnt = Counter([t.status for t in self.tasks])
        status_percent = (
            status_cnt[TASK.TaskStatus.TK_Active] / 2
            + status_cnt[TASK.TaskStatus.TK_Complete]
        ) / len(self.tasks)

        return round(mean([task_dur_percent, status_percent]), 4)

    @cached_property
    def tasks_by_code(self) -> dict[str, TASK]:
        return {task.task_code: task for task in self.tasks}

    @cached_property
    def this_period_cost(self) -> float:
        """Sum of task resource this period costs"""
        return round(sum(task.this_period_cost for task in self.tasks), 2)

    @cached_property
    def wbs_by_path(self) -> dict[str, PROJWBS]:
        return {node.full_code: node for node in self.wbs_nodes}

    def planned_progress(self, before_date: datetime) -> dict[str, list[TASK]]:
        """All planned progress through a given date.

        Args:
            before_date (datetime): End date for planned progress

        Returns:
            dict[str, list[TASK]]: Early and late planned progress during time frame
        """
        progress = {"start": [], "finish": [], "late_start": [], "late_finish": []}

        for task in self.tasks:
            if task.status.is_not_started:
                if task.start < before_date:
                    progress["start"].append(task)

                if task.late_start_date and task.late_start_date < before_date:
                    progress["late_start"].append(task)

            if not task.status.is_completed:
                if task.finish < before_date:
                    progress["finish"].append(task)

                if task.late_end_date and task.late_end_date < before_date:
                    progress["late_finish"].append(task)

        return progress
