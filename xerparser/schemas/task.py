# xerparser
# task.py

from datetime import datetime
from enum import Enum
from functools import cached_property

from xerparser.schemas.actvcode import ACTVCODE
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.taskfin import TASKFIN
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskrsrc import TASKRSRC
from xerparser.scripts.decorators import rounded
from xerparser.src.validators import (
    datetime_or_none,
    date_format,
    float_or_none,
    int_or_none,
    str_or_none,
)


class TASK:
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

    def __init__(self, calendar: CALENDAR | None, wbs: PROJWBS, **data) -> None:

        self.uid: str = data["task_id"]

        # Foreign keys
        self.proj_id: str = data["proj_id"]
        self.wbs_id: str = data["wbs_id"]
        self.clndr_id: str = data["clndr_id"]

        # General Task info
        self.phys_complete_pct: float = float(data["phys_complete_pct"])
        self.complete_pct_type: str = data["complete_pct_type"]
        self.type: TASK.TaskType = TASK.TaskType[data["task_type"]]
        self.status: TASK.TaskStatus = TASK.TaskStatus[data["status_code"]]
        self.task_code: str = data["task_code"]
        self.name: str = data["task_name"]

        # Durations and float
        self.duration_type: str = data["duration_type"]
        self.total_float_hr_cnt: float | None = float_or_none(
            data["total_float_hr_cnt"]
        )
        self.free_float_hr_cnt: float | None = float_or_none(data["free_float_hr_cnt"])
        self.remain_drtn_hr_cnt: float | None = float_or_none(
            data["remain_drtn_hr_cnt"]
        )
        self.target_drtn_hr_cnt: float = float(data["target_drtn_hr_cnt"])
        self.float_path: int | None = int_or_none(data["float_path"])
        self.float_path_order: int | None = int_or_none(data["float_path_order"])
        self.is_longest_path: bool = data["driving_path_flag"] == "Y"

        # Dates
        self.act_start_date: datetime | None = datetime_or_none(data["act_start_date"])
        self.act_end_date: datetime | None = datetime_or_none(data["act_end_date"])
        self.late_start_date: datetime | None = datetime_or_none(
            data["late_start_date"]
        )
        self.late_end_date: datetime | None = datetime_or_none(data["late_end_date"])
        self.expect_end_date: datetime | None = datetime_or_none(
            data["expect_end_date"]
        )
        self.early_start_date: datetime | None = datetime_or_none(
            data["early_start_date"]
        )
        self.early_end_date: datetime | None = datetime_or_none(data["early_end_date"])
        self.rem_late_start_date: datetime | None = datetime_or_none(
            data["rem_late_start_date"]
        )
        self.rem_late_end_date: datetime | None = datetime_or_none(
            data["rem_late_end_date"]
        )
        self.restart_date: datetime | None = datetime_or_none(data["restart_date"])
        self.reend_date: datetime | None = datetime_or_none(data["reend_date"])
        self.target_start_date: datetime = datetime.strptime(
            data["target_start_date"], date_format
        )
        self.target_end_date: datetime = datetime.strptime(
            data["target_end_date"], date_format
        )
        self.suspend_date: datetime | None = datetime_or_none(data["suspend_date"])
        self.resume_date: datetime | None = datetime_or_none(data["resume_date"])
        self.create_date: datetime = datetime.strptime(data["create_date"], date_format)
        self.update_date: datetime = datetime.strptime(data["update_date"], date_format)

        # Constraints
        self.cstr_date: datetime | None = datetime_or_none(data["cstr_date"])
        self.cstr_type: str | None = str_or_none(data["cstr_type"])
        self.cstr_date2: datetime | None = datetime_or_none(data["cstr_date2"])
        self.cstr_type2: str | None = str_or_none(data["cstr_type2"])

        # Unit quantities
        self.target_work_qty: float = float(data["target_work_qty"])
        self.act_work_qty: float = float(data["act_work_qty"])
        self.target_equip_qty: float = float(data["target_equip_qty"])
        self.act_equip_qty: float = float(data["act_equip_qty"])

        # calendar is optional None type for occurances when the
        # xer file is corrupted and task clndr_id references a
        # non-existent calendar.
        self.activity_codes: dict[ACTVTYPE, ACTVCODE] = {}
        self.calendar: CALENDAR | None = calendar
        self.wbs: PROJWBS = self._valid_projwbs(wbs)
        self.memos: list[TASKMEMO] = []
        self.resources: dict[str, TASKRSRC] = {}
        self.predecessors: list["LinkToTask"] = []
        self.successors: list["LinkToTask"] = []
        self.periods: list[TASKFIN] = []

    def __eq__(self, __o: "TASK") -> bool:
        return self.task_code == __o.task_code

    def __lt__(self, __o: "TASK") -> bool:
        return self.task_code < __o.task_code

    def __gt__(self, __o: "TASK") -> bool:
        return self.task_code > __o.task_code

    def __hash__(self) -> int:
        return hash(self.task_code)

    def __str__(self) -> str:
        return f"{self.task_code} - {self.name}"

    @property
    @rounded()
    def actual_cost(self) -> float:
        return sum((res.act_total_cost for res in self.resources.values()))

    @property
    @rounded()
    def at_completion_cost(self) -> float:
        return sum((res.at_completion_cost for res in self.resources.values()))

    @property
    @rounded()
    def budgeted_cost(self) -> float:
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
    def duration(self) -> int:
        """
        Returns remaining duration if task is not started; otherwise, returns original duration.
        """
        # This is usefull when the remaining duration is unlinked from the
        # original duration in the project settings
        # In these cases, the remaining duration can be different to the
        # original duration in tasks that have not started.

        if self.status.is_not_started:
            return self.remaining_duration
        return self.original_duration

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
    def is_critical(self) -> bool:
        return self.total_float_hr_cnt is not None and self.total_float_hr_cnt <= 0

    @property
    def original_duration(self) -> int:
        return int(self.target_drtn_hr_cnt / 8)

    @cached_property
    @rounded(ndigits=4)
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
    @rounded()
    def remaining_cost(self) -> float:
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
        if self.early_start_date:
            return self.early_start_date
        raise ValueError(f"Could not find start date for task {self.task_code}")

    @property
    @rounded()
    def this_period_cost(self) -> float:
        return sum((res.act_this_per_cost for res in self.resources.values()))

    @property
    def total_float(self) -> int | None:
        if self.total_float_hr_cnt is None:
            return
        return int(self.total_float_hr_cnt / 8)

    def _valid_projwbs(self, value: PROJWBS) -> PROJWBS:
        if not isinstance(value, PROJWBS):
            raise ValueError(f"ValueError: expected <class PROJWBS>; got {type(value)}")
        if value.uid != self.wbs_id:
            raise ValueError(
                f"ValueError: WBS unique id {value.uid} does not match wbs_id {self.wbs_id}"
            )
        return value


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
