# xerparser
# trsrcfin.py

from xerparser.schemas.findates import FINDATES
from xerparser.src.validators import float_or_zero


class TRSRCFIN:
    """
    A class to represent a Activity Resource Assignment Past Period Actuals
    """

    def __init__(self, period: FINDATES, **data) -> None:
        self.act_cost: float = float_or_zero(data["act_cost"])
        self.act_qty: float = float_or_zero(data["act_qty"])
        self.fin_dates_id: str = data["fin_dates_id"]
        self.proj_id: str = data["proj_id"]
        self.task_id: str = data["task_id"]
        self.taskrsrc_id: str = data["taskrsrc_id"]
        self.period: FINDATES = self._valid_findates(period)

    def __eq__(self, __o: "TRSRCFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)

    def __gt__(self, __o: "TRSRCFIN") -> bool:
        return self.period > __o.period

    def __lt__(self, __o: "TRSRCFIN") -> bool:
        return self.period < __o.period

    def _valid_findates(self, value: FINDATES) -> FINDATES:
        """Validate assignment of Financial Period"""
        if not isinstance(value, FINDATES):
            raise ValueError(f"Expected <class FINDATES>; got {type(value)}")
        if value.uid != self.fin_dates_id:
            raise ValueError(
                f"FINDATES {value.uid} does not equal fin_dates_id {self.fin_dates_id}"
            )
        return value
