# xerparser
# taskrsrc.py

# from dataclasses import dataclass, field
from datetime import datetime

from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.rsrc import RSRC
from xerparser.schemas.trsrcfin import TRSRCFIN
from xerparser.scripts.decorators import rounded
from xerparser.src.validators import (
    date_format,
    optional_date,
    optional_str,
)


class TASKRSRC:
    """A class to represent a resource assigned to an activity."""

    def __init__(self, account: ACCOUNT | None, resource: RSRC, **data: str) -> None:
        self.uid: str = data["taskrsrc_id"]
        self.task_id: str = data["task_id"]
        self.proj_id: str = data["proj_id"]
        self.acct_id: str | None = optional_str(data["acct_id"])
        self.rsrc_id: str = data["rsrc_id"]
        self.remain_qty: float = float(data["remain_qty"].replace(",", "."))
        self.target_qty: float = float(data["target_qty"].replace(",", "."))
        self.act_ot_qty: float = float(data["act_ot_qty"].replace(",", "."))
        self.act_reg_qty: float = float(data["act_reg_qty"].replace(",", "."))
        self.target_cost: float = float(data["target_cost"].replace(",", "."))
        self.act_reg_cost: float = float(data["act_reg_cost"].replace(",", "."))
        self.act_ot_cost: float = float(data["act_ot_cost"].replace(",", "."))
        self.remain_cost: float = float(data["remain_cost"].replace(",", "."))
        self.act_start_date: datetime | None = optional_date(data["act_start_date"])
        self.act_end_date: datetime | None = optional_date(data["act_end_date"])
        self.restart_date: datetime | None = optional_date(data["restart_date"])
        self.reend_date: datetime | None = optional_date(data["reend_date"])
        self.target_start_date: datetime = datetime.strptime(
            data["target_start_date"], date_format
        )
        self.target_end_date: datetime = datetime.strptime(
            data["target_end_date"], date_format
        )
        self.target_lag_drtn_hr_cnt: int = int(data["target_lag_drtn_hr_cnt"])
        self.rem_late_start_date: datetime | None = optional_date(
            data["rem_late_start_date"]
        )
        self.rem_late_end_date: datetime | None = optional_date(
            data["rem_late_end_date"]
        )
        self.act_this_per_cost: float = float(
            data["act_this_per_cost"].replace(",", ".")
        )
        self.act_this_per_qty: float = float(data["act_this_per_qty"].replace(",", "."))
        self.rsrc_type: str = data["rsrc_type"]
        self.account: ACCOUNT | None = account_or_none(account)
        self.resource: RSRC = resource
        self.periods: list[TRSRCFIN] = []

    def __eq__(self, __o: "TASKRSRC") -> bool:
        return all(
            (
                self.resource == __o.resource,
                self.account == __o.account,
                self.target_qty == __o.target_qty,
                self.target_cost == __o.target_cost,
            )
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.resource,
                self.account,
                self.target_qty,
                self.target_cost,
            )
        )

    @property
    @rounded()
    def act_total_cost(self) -> float:
        return self.act_reg_cost + self.act_ot_cost

    @property
    @rounded()
    def act_total_qty(self) -> float:
        return self.act_reg_qty + self.act_ot_qty

    @property
    def at_completion_cost(self) -> float:
        return self.act_total_cost + self.remain_cost

    @property
    def at_completion_qty(self) -> float:
        return self.act_total_qty + self.remain_qty

    @property
    @rounded(ndigits=4)
    def cost_percent(self) -> float:
        return self.act_total_cost / self.target_cost if self.target_cost else 0.0

    @property
    @rounded()
    def cost_variance(self) -> float:
        return self.at_completion_cost - self.target_cost

    @property
    def finish(self) -> datetime:
        """Calculated Finish Date for task resource (Actual Finish or Early Finish)"""
        if self.act_end_date:
            return self.act_end_date
        if self.reend_date:
            return self.reend_date
        raise ValueError(f"Could not find finish date for taskrsrc {self.uid}")

    @property
    def lag(self) -> int:
        return int(self.target_lag_drtn_hr_cnt / 8)

    @property
    def resource_type(self) -> str | None:
        """Resource type (Labor, Material, Non-Labor)"""
        return self.resource.type[3:] if self.resource else None

    @property
    def start(self) -> datetime:
        """Calculated Start Date for task resource (Actual Start or Early Start)"""
        if self.act_start_date:
            return self.act_start_date
        if self.restart_date:
            return self.restart_date
        raise ValueError(f"Could not find start date for taskrsrc {self.uid}")


def account_or_none(value: ACCOUNT | None) -> ACCOUNT | None:
    if value is None:
        return None
    if not isinstance(value, ACCOUNT):
        raise ValueError(f"ValueError: expected <class ACCOUNT>; got {type(value)}")
    return value
