# xerparser
# trsrcfin.py

from xerparser.schemas.findates import FINDATES


class TRSRCFIN:
    def __init__(self, period: FINDATES, **data) -> None:
        self.act_cost: float = (
            0.0 if data["act_cost"] == "" else float(data["act_cost"])
        )
        self.act_qty: float = 0.0 if data["act_qty"] == "" else float(data["act_qty"])
        self.fin_dates_id: str = data["fin_dates_id"]
        self.proj_id: str = data["proj_id"]
        self.task_id: str = data["task_id"]
        self.taskrsrc_id: str = data["taskrsrc_id"]
        self.period: FINDATES = period

    def __eq__(self, __o: "TRSRCFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)
