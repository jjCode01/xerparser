# xerparser
# taskfin.py

from xerparser.schemas.findates import FINDATES


class TASKFIN:
    def __init__(self, period: FINDATES, **data) -> None:

        self.act_equip_cost: float = _validate_float(data["act_equip_cost"])
        self.act_equip_qty: float = _validate_float(data["act_equip_qty"])
        self.act_expense_cost: float = _validate_float(data["act_expense_cost"])
        self.act_mat_cost: float = _validate_float(data["act_mat_cost"])
        self.act_work_cost: float = _validate_float(data["act_work_cost"])
        self.act_work_qty: float = _validate_float(data["act_work_qty"])
        self.bcwp: float = _validate_float(data["bcwp"])
        self.bcws: float = _validate_float(data["bcws"])
        self.fin_dates_id: str = data["fin_dates_id"]
        self.c: float = _validate_float(data["perfm_work_qty"])
        self.proj_id: str = data["proj_id"]
        self.sched_work_qty: float = _validate_float(data.get("sched_work_qty", ""))
        self.task_id: str = data["task_id"]
        self.period: FINDATES = period

    def __eq__(self, __o: "TASKFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)


def _validate_float(value: str) -> float:
    if value == "" or value == 0:
        return 0.0
    return float(value)
