from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel
from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.rsrc import RSRC


@dataclass
class ResourceValues:
    """
    A class to represent resource cost or unit quantity values.
    """

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


class TASKRSRC(BaseModel):
    """
    A class to represent a resource assigned to a schedule activity.
    """

    taskrsrc_id: str
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
    account: ACCOUNT | None = None
    resource: RSRC = None

    class config:
        arbitrary_types_allowed = True

    def __eq__(self, __o: "TASKRSRC") -> bool:
        return (
            self.task == __o.task
            and self.resource == __o.resource
            and self.account == __o.account
            and self.target_qty == __o.target_qty
            and self.target_lag_drtn_hr_cnt == __o.target_lag_drtn_hr_cnt
            and self.target_cost == __o.target_cost
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.task,
                self.resource,
                self.account,
                self.target_qty,
                self.target_lag_drtn_hr_cnt,
                self.target_cost,
            )
        )

    def __str__(self) -> str:
        return f"{self.task.task_code} | {self.resource.rsrc_name} | ${self.cost.budget:,.2f}"

    @property
    def lag(self) -> int:
        return int(self.target_lag_drtn_hr_cnt / 8)

    @property
    def resource_type(self) -> str:
        """Resource type (Labor, Material, Non-Labor)"""
        return self.resource.rsrc_type[3:]

    @property
    def earned_value(self) -> float:
        return self.cost.budget * self.task.percent_complete

    @property
    def finish(self) -> datetime:
        return (self.act_end_date, self.reend_date)[self.act_end_date is None]

    @property
    def start(self) -> datetime:
        return (self.act_start_date, self.restart_date)[self.act_start_date is None]

    @property
    def cost(self) -> ResourceValues:
        return ResourceValues(
            budget=self.target_cost,
            actual=self.act_reg_cost + self.act_ot_cost,
            this_period=self.act_this_per_cost,
            remaining=self.remain_cost,
        )

    @property
    def unit_qty(self) -> ResourceValues:
        return ResourceValues(
            budget=self.target_qty,
            actual=self.act_reg_qty + self.act_ot_qty,
            this_period=self.act_this_per_qty,
            remaining=self.remain_qty,
        )
