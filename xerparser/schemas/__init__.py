from xerparser.schemas.calendars import SchedCalendar
from xerparser.schemas.project import Project
from xerparser.schemas.projwbs import WbsNode
from xerparser.schemas.task import Task
from xerparser.schemas.taskpred import TaskPred


TABLE_TO_CLASS = {
    "CALENDAR": SchedCalendar,
    "PROJECT": Project,
    "PROJWBS": WbsNode,
    "TASK": Task,
    "TASKPRED": TaskPred,
}
