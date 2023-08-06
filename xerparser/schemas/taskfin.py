# xerparser
# taskfin.py

from xerparser.schemas.findates import FINDATES
from xerparser.src.validators import float_or_zero


class TASKFIN:
    """
    A class to represent a past Finacial Period for an activity
    """

    def __init__(self, period: FINDATES, **data) -> None:
        self.act_equip_cost: float = float_or_zero(data["act_equip_cost"])
        self.act_equip_qty: float = float_or_zero(data["act_equip_qty"])
        self.act_expense_cost: float = float_or_zero(data["act_expense_cost"])
        self.act_mat_cost: float = float_or_zero(data["act_mat_cost"])
        self.act_work_cost: float = float_or_zero(data["act_work_cost"])
        self.act_work_qty: float = float_or_zero(data["act_work_qty"])
        self.bcwp: float = float_or_zero(data["bcwp"])
        self.bcws: float = float_or_zero(data["bcws"])
        self.fin_dates_id: str = data["fin_dates_id"]
        self.perfm_work_qty: float = float_or_zero(data["perfm_work_qty"])
        self.proj_id: str = data["proj_id"]
        self.sched_work_qty: float = float_or_zero(data.get("sched_work_qty", ""))
        self.task_id: str = data["task_id"]
        self.period: FINDATES = period

    def __eq__(self, __o: "TASKFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)

    @property
    def actual_total_cost(self) -> float:
        return (
            self.act_equip_cost
            + self.act_expense_cost
            + self.act_mat_cost
            + self.act_work_cost
        )
