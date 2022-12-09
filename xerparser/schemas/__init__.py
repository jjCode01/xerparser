from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.memotype import MEMOTYPE
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.taskresource import TASKRSRC
from xerparser.schemas.task import TASK
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.rsrc import RSRC


TABLE_MAP = {
    "ACCOUNT": (ACCOUNT, "acct_id"),
    "CALENDAR": (CALENDAR, "clndr_id"),
    "MEMOTYPE": (MEMOTYPE, "memo_type_id"),
    "PROJECT": (PROJECT, "proj_id"),
    "PROJWBS": (PROJWBS, "wbs_id"),
    "RSRC": (RSRC, "rsrc_id"),
    "TASK": (TASK, "task_id"),
    "TASKMEMO": (TASKMEMO, "memo_id"),
    "TASKPRED": (TASKPRED, "task_pred_id"),
    "TASKRSRC": (TASKRSRC, "task_pred_id"),
}
