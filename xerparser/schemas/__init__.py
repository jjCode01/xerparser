from pydantic import BaseModel
from enum import Enum

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

XER_TABLES = ("ACCOUNT", "CALENDAR", "PROJECT", "PROJWBS", "RSRC", "TASK", "TASKPRED")


class Tbl(Enum):
    ACCOUNT = ACCOUNT
    CALENDAR = CALENDAR


class Tables(BaseModel):
    account: list[ACCOUNT] = []
    calendar: list[CALENDAR]
    project: list[PROJECT]
    projwbs: list[PROJWBS]
    rsrc: list[RSRC] = []
    task: list[TASK]
    taskpred: list[TASKPRED]
    taskrsrc: list[TASKRSRC] = []
