# xerparser
# projwbs.py

import itertools
from datetime import datetime
from typing import Any

from xerparser.schemas._node import Node
from xerparser.schemas.task import TASK
from xerparser.schemas.udftype import UDFTYPE
from xerparser.scripts.decorators import rounded
from xerparser.src.validators import int_or_zero, optional_int


class PROJWBS(Node):
    """
    A class to represent a schedule WBS node.
    """

    def __init__(self, project, **data: str) -> None:
        from xerparser.schemas.project import PROJECT

        super().__init__(
            data["wbs_id"],
            data["wbs_short_name"],
            data["wbs_name"],
            data["parent_wbs_id"],
            int_or_zero(data["seq_num"]),
        )
        self.is_proj_node: bool = data["proj_node_flag"] == "Y"
        """Project Level Code Flag"""
        self.proj_id: str = data["proj_id"]
        """Foreign Key for `PROJECT` WBS node belongs to"""
        self.project: PROJECT = project
        self.seq_num: int | None = optional_int(data["seq_num"])
        """Sort Order"""
        self.status_code: str = data["status_code"]

        self.user_defined_fields: dict[UDFTYPE, Any] = {}
        self._tasks: dict[str, TASK] = {}

        self.project.wbs_nodes.append(self)
        if self.is_proj_node:
            self.project.wbs_root = self

    @property
    @rounded()
    def actual_cost(self) -> float:
        """Sum of task resource actual costs"""
        return sum(task.actual_cost for task in self.all_tasks)

    @property
    def actual_duration(self) -> int:
        if not (_start := self.start) or not (_finish := self.finish):
            return 0
        if _finish < self.project.data_date:
            return self.original_duration
        return max((0, (self.project.data_date.date() - _start.date()).days))

    @property
    def all_tasks(self) -> list[TASK]:
        return list(
            itertools.chain.from_iterable(
                [node.tasks for node in self.traverse_children()]
            )
        )

    @property
    def assignments(self) -> int:
        """Activity Assignment Count"""
        return len(self.tasks)

    @property
    @rounded()
    def budgeted_cost(self) -> float:
        """Sum of task budgeted costs"""
        return sum(task.budgeted_cost for task in self.all_tasks)

    @property
    @rounded()
    def cost_variance(self) -> float:
        return sum(task.cost_variance for task in self.all_tasks)

    @property
    def lineage(self) -> list["PROJWBS"]:
        if self.is_proj_node:
            return []

        if not self._parent:
            return [self]

        return self._parent.lineage + [self]

    @property
    def finish(self) -> datetime | None:
        return max((task.finish for task in self.all_tasks), default=None)

    @property
    def full_code(self) -> str:
        return ".".join([node.code for node in self.lineage])

    @property
    def late_finish(self) -> datetime | None:
        return max(
            (task.late_end_date for task in self.all_tasks if task.late_end_date),
            default=self.finish,
        )

    @property
    def late_start(self) -> datetime | None:
        return min(
            (task.late_start_date for task in self.all_tasks if task.late_start_date),
            default=self.start,
        )

    @property
    def original_duration(self) -> int:
        if not (_start := self.start) or not (_finish := self.finish):
            return 0
        return (_finish.date() - _start.date()).days

    @property
    @rounded()
    def remaining_cost(self) -> float:
        """Sum of task resource remaining costs"""
        return sum(task.remaining_cost for task in self.all_tasks)

    @property
    def remaining_duration(self) -> int:
        if not (_start := self.start) or not (_finish := self.finish):
            return 0
        if _start >= self.project.data_date:
            return self.original_duration
        return max((0, (_finish.date() - self.project.data_date.date()).days))

    @property
    def start(self) -> datetime | None:
        return min((task.start for task in self.all_tasks), default=None)

    @property
    def tasks(self) -> list[TASK]:
        return list(self._tasks.values())

    @property
    @rounded()
    def this_period_cost(self) -> float:
        """Sum of task this period costs"""
        return sum((task.this_period_cost for task in self.all_tasks), 0.0)

    def add_task(self, task: TASK):
        self._tasks[task.uid] = task
