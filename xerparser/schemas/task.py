from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from xerparser.schemas import CALENDAR, PROJWBS


class ConstraintType(Enum):
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
    CP_Phys = "Physical"
    CP_Drtn = "Duration"
    CP_Units = "Unit"


class TaskStatus(Enum):
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


class TASK(BaseModel):
    task_id: str
    proj_id: str
    wbs_id: str
    clndr_id: str
    phys_complete_pct: float
    complete_pct_type: str
    task_type: str
    duration_type: str
    status_code: str
    task_code: str
    task_name: str
    total_float_hr_cnt: float | None
    free_float_hr_cnt: float | None
    remain_drtn_hr_cnt: float | None
    target_drtn_hr_cnt: float | None
    cstr_date: datetime | None
    act_start_date: datetime | None
    act_end_date: datetime | None
    late_start_date: datetime | None
    late_end_date: datetime | None
    expect_end_date: datetime | None
    early_start_date: datetime | None
    early_end_date: datetime | None
    restart_date: datetime | None
    reend_date: datetime | None
    target_start_date: datetime
    target_end_date: datetime
    target_work_qty: float
    act_work_qty: float
    target_equip_qty: float
    act_equip_qty: float
    rem_late_start_date: datetime | None
    rem_late_end_date: datetime | None
    cstr_type: str | None
    suspend_date: datetime | None
    resume_date: datetime | None
    float_path: int | None
    float_path_order: int | None
    cstr_date2: datetime | None
    cstr_type2: str | None
    driving_path_flag: str
    create_date: datetime
    update_date: datetime
    calendar: CALENDAR = None
    wbs: PROJWBS = None

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, __o: "TASK") -> bool:
        return self.task_code == __o.task_code

    def __hash__(self) -> int:
        return hash(self.task_code)

    def __str__(self) -> str:
        return f"{self.task_code} - {self.task_name}"

    @property
    def constraints(self) -> dict:
        return {
            "prime": {
                "type": ConstraintType[self.cstr_type] if self.cstr_type else None,
                "date": self.cstr_date,
            },
            "second": {
                "type": ConstraintType[self.cstr_type2] if self.cstr_type2 else None,
                "date": self.cstr_date2,
            },
        }

    @property
    def finish(self) -> datetime:
        return (self.early_end_date, self.act_end_date)[self.status.is_completed]

    @property
    def free_float(self) -> int | None:
        return (self.free_float_hr_cnt / 8, None)[self.status.is_completed]

    @property
    def is_critical(self) -> bool:
        return not self.status.is_completed and self.total_float_hr_cnt <= 0

    @property
    def is_longest_path(self) -> bool:
        return self.driving_path_flag == "Y"

    @property
    def original_duration(self) -> int:
        return int(self.target_drtn_hr_cnt / 8)

    @property
    def percent_complete(self) -> float:
        if self.percent_type is PercentType.CP_Phys:
            return self.phys_complete_pct / 100

        if self.percent_type is PercentType.CP_Drtn:
            if self.status.is_not_started or self.original_duration == 0:
                return 0.0
            if self.status.is_completed:
                return 1.0
            if self.remain_drtn_hr_cnt >= self.target_drtn_hr_cnt:
                return 0.0

            return 1 - self.remain_drtn_hr_cnt / self.target_drtn_hr_cnt

        if self.percent_type is PercentType.CP_Units:
            target_units = self.target_work_qty + self.target_equip_qty
            if target_units == 0:
                return 0.0
            actual_units = self.act_work_qty + self.act_equip_qty
            return 1 - actual_units / target_units

    @property
    def percent_type(self) -> PercentType:
        return PercentType[self.complete_pct_type]

    @property
    def remaining_duration(self) -> int:
        return int(self.remain_drtn_hr_cnt / 8)

    @property
    def start(self) -> datetime:
        return (self.act_start_date, self.early_start_date)[self.status.is_not_started]

    @property
    def status(self) -> TaskStatus:
        return TaskStatus[self.status_code]

    @property
    def total_float(self) -> int | None:
        if self.total_float_hr_cnt is None:
            return
        return int(self.total_float_hr_cnt / 8)

    @property
    def type(self) -> TaskType:
        return TaskType[self.task_type]
