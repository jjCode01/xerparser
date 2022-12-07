from pydantic import BaseModel

from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.resource import RSRC, TASKRSRC, ACCOUNT
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED


TABLE_TO_CLASS = {
    "ACCOUNT": ACCOUNT,
    "CALENDAR": CALENDAR,
    "PROJECT": PROJECT,
    "PROJWBS": PROJWBS,
    "RSRC": RSRC,
    "TASK": TASK,
    "TASKPRED": TASKPRED,
}


class Tables(BaseModel):
    account: list[ACCOUNT] = []
    calendar: list[CALENDAR]
    project: list[PROJECT]
    projwbs: list[PROJWBS]
    rsrc: list[RSRC] = []
    task: list[TASK]
    taskpred: list[TASKPRED]
    taskrsrc: list[TASKRSRC] = []
