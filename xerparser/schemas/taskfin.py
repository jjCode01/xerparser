# xerparser
# taskfin.py

from pydantic import BaseModel, validator
from xerparser.schemas.findates import FINDATES

empty_to_zero = (
    "act_equip_cost",
    "act_equip_qty",
    "act_expense_cost",
    "act_mat_cost",
    "act_work_cost",
    "act_work_qty",
    "bcwp",
    "bcws",
    "sched_work_qty",
    "perfm_work_qty",
)


class TASKFIN(BaseModel):
    act_equip_cost: float  # Actual Nonlabor Cost
    act_equip_qty: float  # Actual Nonlabor Units
    act_expense_cost: float  # Actual Expense Cost
    act_mat_cost: float  # Actual Material Cost
    act_work_cost: float  # Actual Labor Cost
    act_work_qty: float  # Actual Labor Units
    bcwp: float  # Earned Value Cost
    bcws: float  # Planned Value Cost
    fin_dates_id: str  # Financial Period Unique ID
    perfm_work_qty: float  # Earned Value Labor Units
    proj_id: str  # Project Unique ID
    sched_work_qty: float = 0.0  # Planned Value Labor Units
    task_id: str  # Activity Unique ID
    period: FINDATES

    @validator(*empty_to_zero, pre=True)
    def empty_to_float(value):
        if value == "" or value == 0:
            return 0.0

        return value

    def __eq__(self, __o: "TASKFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)
