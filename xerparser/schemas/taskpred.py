# xerparser
# taskpred.py

from datetime import datetime
from xerparser.schemas.task import TASK
from xerparser.src.validators import optional_int, optional_date, int_or_zero


class TASKPRED:
    """
    A class to represent a relationship between two activities.

    """

    def __init__(self, predecessor: TASK, successor: TASK, **data) -> None:
        self.uid: str = data["task_pred_id"]
        self.task_id: str = data["task_id"]
        self.pred_task_id: str = data["pred_task_id"]
        self.proj_id: str = data["proj_id"]
        self.pred_proj_id: str = data["pred_proj_id"]
        self.pred_type: str = data["pred_type"]
        self.lag_hr_cnt: int = int_or_zero(data["lag_hr_cnt"])
        self.float_path: int | None = optional_int(data["float_path"])
        self.aref: datetime | None = optional_date(data["aref"])
        self.arls: datetime | None = optional_date(data["arls"])
        self.predecessor: TASK = predecessor
        self.successor: TASK = successor

    def __eq__(self, __o: "TASKPRED") -> bool:
        return (
            self.predecessor == __o.predecessor
            and self.successor == __o.successor
            and self.link == __o.link
        )

    def __gt__(self, __o: "TASKPRED") -> bool:
        if self.predecessor == __o.predecessor:
            if self.successor == __o.successor:
                return self.link > __o.link
            return self.successor > __o.successor
        return self.predecessor > __o.predecessor

    def __lt__(self, __o: "TASKPRED") -> bool:
        if self.predecessor == __o.predecessor:
            if self.successor == __o.successor:
                return self.link < __o.link
            return self.successor < __o.successor
        return self.predecessor < __o.predecessor

    def __hash__(self) -> int:
        return hash((self.predecessor, self.successor, self.link))

    @property
    def lag(self) -> int:
        return int(self.lag_hr_cnt / 8)

    @property
    def link(self) -> str:
        return self.pred_type[-2:]
