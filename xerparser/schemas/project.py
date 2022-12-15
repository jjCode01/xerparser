# xerparser
# project.py

from datetime import datetime
from functools import cached_property
from pydantic import BaseModel, Field, validator
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.task import TASK
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.taskrsrc import TASKRSRC

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
    name: str = ""
    tasks: dict[str, TASK] = {}
    relationships: dict[str, TASKPRED] = {}
    wbs: dict[str, PROJWBS] = {}

    @validator("export_flag", pre=True)
    def flag_to_bool(cls, value):
        return value == "Y"

    @validator(*field_can_be_none, pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @property
    def actual_cost(self) -> float:
        if not self.tasks:
            return 0.0
        return sum((task.actual_cost for task in self.tasks.values()))

    @property
    def actual_start(self) -> datetime:
        if not self.tasks:
            return self.plan_start_date
        return min((task.start for task in self.tasks.values()))

    @property
    def budgeted_cost(self) -> float:
        if not self.tasks:
            return 0.0
        return sum((task.budgeted_cost for task in self.tasks.values()))

    @property
    def original_duration(self) -> int:
        return self.finish_date - self.actual_start

    @property
    def remaining_cost(self) -> float:
        if not self.tasks:
            return 0.0
        return sum((task.remaining_cost for task in self.tasks.values()))

    @property
    def remaining_duration(self) -> int:
        if self.data_date >= self.finish_date:
            return 0

        return (self.finish_date - self.data_date).days

    @property
    def this_period_cost(self) -> float:
        if not self.tasks:
            return 0.0
        return sum((task.this_period_cost for task in self.tasks.values()))
