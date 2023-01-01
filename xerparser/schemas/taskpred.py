# xerparser
# taskpred.py

from datetime import datetime
from xerparser.schemas.task import TASK


class TASKPRED:
    """A class to represent a relationship between two activities."""

    def __init__(self, predecessor: TASK, successor: TASK, **data) -> None:

        self.uid: str = data["task_pred_id"]
        self.task_id: str = data["task_id"]
        self.pred_task_id: str = data["pred_task_id"]
        self.proj_id: str = data["proj_id"]
        self.pred_proj_id: str = data["pred_proj_id"]
        self.pred_type: str = data["pred_type"]
        self.lag_hr_cnt: int = int(data["lag_hr_cnt"])
        self.float_path: int | None = (
            None if data["float_path"] == "" else int(data["float_path"])
        )
        self.aref: datetime | None = _datetime_or_none(data["aref"])
        self.arls: datetime | None = _datetime_or_none(data["arls"])
        self.predecessor: TASK = predecessor
        self.successor: TASK = successor

    def __eq__(self, __o: "TASKPRED") -> bool:
        return (
            self.predecessor == __o.predecessor
            and self.successor == __o.successor
            and self.link == __o.link
        )

    def __hash__(self) -> int:
        return hash((self.predecessor, self.successor, self.link))

    @property
    def lag(self) -> int:
        return int(self.lag_hr_cnt / 8)

    @property
    def link(self) -> str:
        return self.pred_type[-2:]


def _datetime_or_none(value: str) -> datetime | None:
    if value == "":
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M")
