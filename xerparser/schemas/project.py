from datetime import datetime
from pydantic import BaseModel


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
