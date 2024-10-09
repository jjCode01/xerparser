# xerparser
# projwbs.py

from typing import Any

from xerparser.schemas._node import Node
from xerparser.schemas.udftype import UDFTYPE
from xerparser.src.validators import int_or_zero, optional_int


class PROJWBS(Node):
    """
    A class to represent a schedule WBS node.
    """

    def __init__(self, **data: str) -> None:
        from xerparser.schemas.task import TASK

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

        self.tasks: list[TASK] = []
        self.user_defined_fields: dict[UDFTYPE, Any] = {}

    @property
    def assignments(self) -> int:
        """Activity Assignment Count"""
        return len(self.tasks)

    @property
    def lineage(self) -> list["PROJWBS"]:
        if self.is_proj_node:
            return []

        if not self._parent:
            return [self]

        return self._parent.lineage + [self]

    @property
    def full_code(self) -> str:
        return ".".join([node.code for node in self.lineage])
