# xerparser
# taskrsrc.py

from dataclasses import dataclass, field
from datetime import datetime

# from functools import cached_property
from pydantic import BaseModel, Field, validator
from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.rsrc import RSRC


@dataclass
class ResourceValues:
    """A class to represent resource cost or unit quantity values."""

    budget: float
    actual: float
    this_period: float
    remaining: float
    at_completion: float = field(init=False)
    variance: float = field(init=False)
    percent: float = field(init=False)

    def __post_init__(self):
        self.at_completion = self.actual + self.remaining
        self.variance = round(self.at_completion - self.budget, 2)
        self.percent = 0.0 if self.budget == 0.0 else self.actual / self.budget

    def __bool__(self) -> bool:
        return self.budget and self.actual


field_can_be_none = (
    "acct_id",
    "act_start_date",
    "act_end_date",
    "restart_date",
    "reend_date",
    "rem_late_start_date",
    "rem_late_end_date",
)


class TASKRSRC(BaseModel):
    """A class to represent a resource assigned to an activity."""

    uid: str = Field(alias="taskrsrc_id")
    task_id: str
    proj_id: str
    acct_id: str | None
    rsrc_id: str
    remain_qty: float
    target_qty: float
    act_ot_qty: float
    act_reg_qty: float
    target_cost: float
    act_reg_cost: float
    act_ot_cost: float
    remain_cost: float
    act_start_date: datetime | None
    act_end_date: datetime | None
    restart_date: datetime | None
    reend_date: datetime | None
    target_start_date: datetime
    target_end_date: datetime
    target_lag_drtn_hr_cnt: int
    rem_late_start_date: datetime | None
    rem_late_end_date: datetime | None
    act_this_per_cost: float
    act_this_per_qty: float
    rsrc_type: str
    account: ACCOUNT | None
    resource: RSRC | None

    class config:
        arbitrary_types_allowed = True
        # keep_untouched = (cached_property,)

    @validator(*field_can_be_none, pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

    def __eq__(self, __o: "TASKRSRC") -> bool:
        return (
            self.resource == __o.resource
            and self.account == __o.account
            and self.target_qty == __o.target_qty
            and self.target_lag_drtn_hr_cnt == __o.target_lag_drtn_hr_cnt
            and self.target_cost == __o.target_cost
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.resource,
                self.account,
                self.target_qty,
                self.target_lag_drtn_hr_cnt,
                self.target_cost,
            )
        )

    @property
    def act_total_cost(self) -> float:
        return self.act_reg_cost + self.act_ot_cost

    @property
    def act_total_qty(self) -> float:
        return self.act_reg_qty + self.act_ot_qty

    @property
    def at_completion_cost(self) -> float:
        return self.act_total_cost + self.remain_cost

    @property
    def at_completion_qty(self) -> float:
        return self.act_total_qty + self.remain_qty

    @property
    def cost_percent(self) -> float:
        return (
            0.0 if self.target_cost == 0.0 else self.act_total_cost / self.target_cost
        )

    @property
    def cost_variance(self) -> float:
        return round(self.at_completion_cost - self.target_cost, 2)

    @property
    def finish(self) -> datetime:
        return (self.act_end_date, self.reend_date)[self.act_end_date is None]

    @property
    def lag(self) -> int:
        return int(self.target_lag_drtn_hr_cnt / 8)

    @property
    def resource_type(self) -> str:
        """Resource type (Labor, Material, Non-Labor)"""
        return self.resource.type[3:]

    @property
    def start(self) -> datetime:
        return (self.act_start_date, self.restart_date)[self.act_start_date is None]
