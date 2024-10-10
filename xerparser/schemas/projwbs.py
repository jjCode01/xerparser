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

    def __init__(self, **data: str) -> None:
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
        self.seq_num: int | None = optional_int(data["seq_num"])
        """Sort Order"""
        self.status_code: str = data["status_code"]

        self.user_defined_fields: dict[UDFTYPE, Any] = {}
        self._tasks: dict[str, TASK] = {}

    @property
    @rounded()
    def actual_cost(self) -> float:
        """Sum of task resource actual costs"""
        return sum(task.actual_cost for task in self.all_tasks)

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
    def lineage(self) -> list["PROJWBS"]:
        if self.is_proj_node:
            return []

        if not self._parent:
            return [self]

        return self._parent.lineage + [self]

    @property
    def finish(self) -> datetime | None:
        if not (_all_tasks := self.all_tasks):
            return None
        return max((task.finish for task in _all_tasks))

    @property
    def full_code(self) -> str:
        return ".".join([node.code for node in self.lineage])

    @property
    @rounded()
    def remaining_cost(self) -> float:
        """Sum of task resource remaining costs"""
        return sum(task.remaining_cost for task in self.all_tasks)

    @property
    def start(self) -> datetime | None:
        if not (_all_tasks := self.all_tasks):
            return None
        return min((task.start for task in _all_tasks))

    @property
    def tasks(self) -> list[TASK]:
        return list(self._tasks.values())

    @property
    @rounded()
    def this_period_cost(self) -> float:
        """Sum of task this period costs"""
        return sum(task.this_period_cost for task in self.all_tasks)

    def add_task(self, task: TASK):
        self._tasks[task.uid] = task
