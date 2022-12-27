# xerparser
# taskpred.py

from datetime import datetime
from pydantic import BaseModel, Field, validator
from xerparser.schemas.task import TASK


class TASKPRED(BaseModel):
    """A class to represent a relationship between two activities."""

    uid: str = Field(alias="task_pred_id")
    task_id: str
    pred_task_id: str
    proj_id: str
    pred_proj_id: str
    pred_type: str
    lag_hr_cnt: int
    float_path: int | None
    aref: datetime | None
    arls: datetime | None
    predecessor: TASK | None = None
    successor: TASK | None = None

    class Config:
        arbitrary_types_allowed = True

    @validator("float_path", "aref", "arls", pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

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
