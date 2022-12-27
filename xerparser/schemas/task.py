# xerparser
# task.py

from datetime import datetime
from enum import Enum
from functools import cached_property
from pydantic import BaseModel, Field, validator

from xerparser.schemas.actvcode import ACTVCODE
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.taskfin import TASKFIN
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskrsrc import TASKRSRC


# Passed to pydantic validator to convert any emtpy strings to None
field_can_be_none = (
    "total_float_hr_cnt",
    "free_float_hr_cnt",
    "remain_drtn_hr_cnt",
    "target_drtn_hr_cnt",
    "cstr_date",
    "act_start_date",
    "act_end_date",
    "late_start_date",
    "late_end_date",
    "expect_end_date",
    "early_start_date",
    "early_end_date",
    "restart_date",
    "reend_date",
    "rem_late_start_date",
    "rem_late_end_date",
    "cstr_type",
    "suspend_date",
    "resume_date",
    "float_path",
    "float_path_order",
    "cstr_date2",
    "cstr_type2",
)


class TASK(BaseModel):
    """
    A class to represent a scehdule activity.
    """

    class ConstraintType(Enum):
        """Map codes used for constraint types to readable descriptions"""

        CS_ALAP = "As Late as Possible"
        CS_MEO = "Finish On"
        CS_MEOA = "Finish on or After"
        CS_MEOB = "Finish on or Before"
        CS_MANDFIN = "Mandatory Finish"
        CS_MANDSTART = "Mandatory Start"
        CS_MSO = "Start On"
        CS_MSOA = "Start On or After"
        CS_MSOB = "Start On or Before"

    class PercentType(Enum):
        """Map codes used for percent types to readable descriptions"""

        CP_Phys = "Physical"
        CP_Drtn = "Duration"
        CP_Units = "Unit"

    class TaskStatus(Enum):
        """Map codes used for Task status to readable descriptions"""

        TK_NotStart = "Not Started"
        TK_Active = "In Progress"
        TK_Complete = "Complete"

        @property
        def is_not_started(self) -> bool:
            return self is self.TK_NotStart

        @property
        def is_in_progress(self) -> bool:
            return self is self.TK_Active

        @property
        def is_completed(self) -> bool:
            return self is self.TK_Complete

        @property
        def is_open(self) -> bool:
            return self is not self.TK_Complete

    class TaskType(Enum):
        """Map codes used for Task types to readable descriptions"""

        TT_Mile = "Start Milestone"
        TT_FinMile = "Finish Milestone"
        TT_LOE = "Level of Effort"
        TT_Task = "Task Dependent"
        TT_Rsrc = "Resource Dependent"
        TT_WBS = "WBS Summary"

        @property
        def is_milestone(self) -> bool:
            return self is self.TT_FinMile or self is self.TT_Mile

        @property
        def is_loe(self) -> bool:
            return self is self.TT_LOE

        @property
        def is_task(self) -> bool:
            return self is self.TT_Task

    uid: str = Field(alias="task_id")

    # Foreign keys
    proj_id: str
    wbs_id: str
    clndr_id: str

    # General Task info
    phys_complete_pct: float
    complete_pct_type: str
    type: TaskType = Field(alias="task_type")
    status: TaskStatus = Field(alias="status_code")
    task_code: str
    name: str = Field(alias="task_name")

    # Durations and float
    duration_type: str
    total_float_hr_cnt: float | None
    free_float_hr_cnt: float | None
    remain_drtn_hr_cnt: float | None
    target_drtn_hr_cnt: float
    float_path: int | None
    float_path_order: int | None
    is_longest_path: bool = Field(alias="driving_path_flag")

    # Dates
    act_start_date: datetime | None
    act_end_date: datetime | None
    late_start_date: datetime | None
    late_end_date: datetime | None
    expect_end_date: datetime | None
    early_start_date: datetime | None
    early_end_date: datetime | None
    rem_late_start_date: datetime | None
    rem_late_end_date: datetime | None
    restart_date: datetime | None
    reend_date: datetime | None
    target_start_date: datetime
    target_end_date: datetime
    suspend_date: datetime | None
    resume_date: datetime | None
    create_date: datetime
    update_date: datetime

    # Constraints
    cstr_date: datetime | None
    cstr_type: str | None
    cstr_date2: datetime | None
    cstr_type2: str | None

    # Unit quantities
    target_work_qty: float
    act_work_qty: float
    target_equip_qty: float
    act_equip_qty: float

    # calendar is optional None type for occurances when the
    # xer file is corrupted and task clndr_id references a
    # non-existent calendar.
    activity_codes: dict[ACTVTYPE, ACTVCODE] = {}
    calendar: CALENDAR | None = None
    wbs: PROJWBS | None = None
    memos: list[TASKMEMO] = []
    resources: dict[str, TASKRSRC] = {}
    predecessors: list["LinkToTask"] = []
    successors: list["LinkToTask"] = []
    periods: list[TASKFIN] = []

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @validator("is_longest_path", pre=True)
    def flag_to_bool(cls, value):
        return value == "Y"

    @validator(*field_can_be_none, pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

    @validator("type", pre=True)
    def type_to_tasktype(cls, value):
        return TASK.TaskType[value]

    @validator("status", pre=True)
    def status_to_taskstatus(cls, value):
        return TASK.TaskStatus[value]

    def __eq__(self, __o: "TASK") -> bool:
        return self.task_code == __o.task_code

    def __hash__(self) -> int:
        return hash(self.task_code)

    def __str__(self) -> str:
        return f"{self.task_code} - {self.name}"

    @property
    def actual_cost(self) -> float:
        if not self.resources:
            return 0.0
        return sum((res.act_total_cost for res in self.resources.values()))

    @property
    def budgeted_cost(self) -> float:
        if not self.resources:
            return 0.0
        return sum((res.target_cost for res in self.resources.values()))

    @property
    def constraints(self) -> dict:
        return {
            "prime": {
                "type": TASK.ConstraintType[self.cstr_type] if self.cstr_type else None,
                "date": self.cstr_date,
            },
            "second": {
                "type": TASK.ConstraintType[self.cstr_type2]
                if self.cstr_type2
                else None,
                "date": self.cstr_date2,
            },
        }

    @property
    def finish(self) -> datetime:
        """Calculated activity finish date (Actual Finish or Early Finish)"""
        if self.act_end_date:
            return self.act_end_date
        if self.early_end_date:
            return self.early_end_date
        raise ValueError(f"Could not find finish date for task {self.task_code}")

    @property
    def free_float(self) -> int | None:
        if not self.free_float_hr_cnt:
            return None

        return int(self.free_float_hr_cnt / 8)

    @property
    def has_predecessor(self) -> bool:
        return len(self.predecessors) > 0

    @property
    def has_successor(self) -> bool:
        return len(self.successors) > 0

    @property
    def has_finish_successor(self) -> bool:
        if not self.has_successor:
            return True

        for succ in self.successors:
            if succ.link in ("FS", "FF"):
                return True

        return False

    @property
    def has_start_predecessor(self) -> bool:
        if not self.has_predecessor:
            return True

        for pred in self.predecessors:
            if pred.link in ("FS", "SS"):
                return True

        return False

    @property
    def is_critical(self) -> bool:
        return self.total_float_hr_cnt is not None and self.total_float_hr_cnt <= 0

    @property
    def original_duration(self) -> int:
        return int(self.target_drtn_hr_cnt / 8)

    @cached_property
    def percent_complete(self) -> float:
        if self.percent_type is TASK.PercentType.CP_Phys:
            return self.phys_complete_pct / 100

        elif self.percent_type is TASK.PercentType.CP_Drtn:
            if self.remain_drtn_hr_cnt is None or self.status.is_completed:
                return 1.0
            if self.status.is_not_started or self.original_duration == 0:
                return 0.0
            if self.remain_drtn_hr_cnt >= self.target_drtn_hr_cnt:
                return 0.0

            return 1 - self.remain_drtn_hr_cnt / self.target_drtn_hr_cnt

        elif self.percent_type is TASK.PercentType.CP_Units:
            target_units = self.target_work_qty + self.target_equip_qty
            if target_units == 0:
                return 0.0
            actual_units = self.act_work_qty + self.act_equip_qty
            return 1 - actual_units / target_units

        raise ValueError(
            f"Could not calculate percent compelete for task {self.task_code}"
        )

    @property
    def percent_type(self) -> PercentType:
        return TASK.PercentType[self.complete_pct_type]

    @property
    def remaining_cost(self) -> float:
        if not self.resources:
            return 0.0
        return sum((res.remain_cost for res in self.resources.values()))

    @property
    def remaining_duration(self) -> int:
        if self.remain_drtn_hr_cnt is None:
            return 0
        return int(self.remain_drtn_hr_cnt / 8)

    @property
    def start(self) -> datetime:
        """Calculated activity start date (Actual Start or Early Start)"""
        if self.act_start_date:
            return self.act_start_date
        if self.early_end_date:
            return self.early_end_date
        raise ValueError(f"Could not find start date for task {self.task_code}")

    @property
    def this_period_cost(self) -> float:
        if not self.resources:
            return 0.0
        return sum((res.act_this_per_cost for res in self.resources.values()))

    @property
    def total_float(self) -> int | None:
        if self.total_float_hr_cnt is None:
            return
        return int(self.total_float_hr_cnt / 8)


class LinkToTask:
    """
    A class to represent a logic tie to another activity
    """

    def __init__(self, task: TASK, link: str, lag_days: int) -> None:
        if link.upper() not in ("FF", "FS", "SF", "SS"):
            raise AttributeError(
                f"link attribute must have a value FF, FS, SF, or SS; got {link}"
            )
        self.task: TASK = task
        self.link: str = link
        self.lag: int = lag_days

    def __eq__(self, __o: "LinkToTask") -> bool:
        return all((self.task == __o.task, self.link == __o.link))

    def __hash__(self) -> int:
        return hash((self.task, self.link))
