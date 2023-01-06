# xerparser
# trsrcfin.py

from xerparser.schemas.findates import FINDATES
from xerparser.src.validators import float_or_zero


class TRSRCFIN:
    def __init__(self, period: FINDATES, **data) -> None:
        self.act_cost: float = float_or_zero(data["act_cost"])
        self.act_qty: float = float_or_zero(data["act_qty"])
        self.fin_dates_id: str = data["fin_dates_id"]
        self.proj_id: str = data["proj_id"]
        self.task_id: str = data["task_id"]
        self.taskrsrc_id: str = data["taskrsrc_id"]
        self.period: FINDATES = valid_findates(period)

    def __eq__(self, __o: "TRSRCFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)


def valid_findates(value: FINDATES) -> FINDATES:
    if not isinstance(value, FINDATES):
        raise ValueError(f"ValueError: expected <class FINDATES>; got {type(value)}")
    return value
