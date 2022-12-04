from datetime import datetime

from pydantic import BaseModel
from xerparser.schemas.task import Task


class TaskPred(BaseModel):
    task_pred_id: str
    task_id: str
    pred_task_id: str
    proj_id: str
    pred_proj_id: str
    pred_type: str
    lag_hr_cnt: int
    float_path: int | None
    aref: datetime | None
    arls: datetime | None
    predecessor: Task = None
    successor: Task = None

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, __o: "TaskPred") -> bool:
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
