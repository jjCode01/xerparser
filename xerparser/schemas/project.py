from datetime import datetime
from pydantic import BaseModel
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED


class PROJECT(BaseModel):
    proj_id: str
    project_flag: str
    proj_short_name: str
    last_recalc_date: datetime
    plan_start_date: datetime
    plan_end_date: datetime | None
    scd_end_date: datetime
    add_date: datetime
    last_fin_dates_id: str | None
    last_schedule_date: datetime | None
    export_flag: str
    name: str = ""
    wbs: dict[str, PROJWBS] = None
    tasks: tuple[TASK] = None
    relationships: tuple[TASKPRED] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def budgeted_cost(self) -> float:
        if not self.tasks:
            return 0.0

        return sum((task.budgeted_cost for task in self.tasks))
