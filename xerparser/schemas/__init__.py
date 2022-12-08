from pydantic import BaseModel
from enum import Enum

from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.memo import MEMOTYPE, TASKMEMO
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.resource import RSRC, TASKRSRC, ACCOUNT
from xerparser.schemas.task import TASK
from xerparser.schemas.taskpred import TASKPRED


TABLE_MAP = {
    "ACCOUNT": ACCOUNT,
    "CALENDAR": CALENDAR,
    "PROJECT": PROJECT,
    "PROJWBS": PROJWBS,
    "RSRC": RSRC,
    "TASK": TASK,
    "TASKPRED": TASKPRED,
}


class TableMap(Enum):
    ACCOUNT = ACCOUNT
    CALENDAR = CALENDAR
    MEMOTYPE = MEMOTYPE
    PROJECT = PROJECT
    PROJWBS = PROJWBS
    RSRC = RSRC
    TASK = TASK
    TASKMEMO = TASKMEMO
    TASKPRED = TASKPRED


class XerTables(BaseModel):
    account: list[ACCOUNT] = []
    calendar: list[CALENDAR]
    project: list[PROJECT]
    projwbs: list[PROJWBS]
    rsrc: list[RSRC] = []
    task: list[TASK]
    taskpred: list[TASKPRED]
    taskrsrc: list[TASKRSRC] = []
