# xerparser
# trsrcfin.py

from pydantic import BaseModel, validator
from xerparser.schemas.findates import FINDATES


class TRSRCFIN(BaseModel):
    act_cost: float
    act_qty: float
    fin_dates_id: str
    proj_id: str
    task_id: str
    taskrsrc_id: str
    period: FINDATES

    @validator("act_cost", "act_qty", pre=True)
    def empty_to_float(value):
        if value == "":
            return 0.0

        return value

    def __eq__(self, __o: "TRSRCFIN") -> bool:
        return self.period == __o.period

    def __hash__(self) -> int:
        return hash(self.period)
