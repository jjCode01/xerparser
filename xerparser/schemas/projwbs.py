# xerparser
# projwbs.py

from typing import Any

from xerparser.schemas._node import Node
from xerparser.schemas.udftype import UDFTYPE
from xerparser.src.validators import optional_int


class PROJWBS(Node):
    """
    A class to represent a schedule WBS node.
    """

    def __init__(self, **data: str) -> None:
        super().__init__()
        self.uid: str = data["wbs_id"]
        """Unique Table ID"""
        self.code: str = data["wbs_short_name"]
        """WBS Code"""
        self.is_proj_node: bool = data["proj_node_flag"] == "Y"
        """Project Level Code Flag"""
        self.name: str = data["wbs_name"]
        """WBS Name"""
        self.parent_wbs_id: str = data["parent_wbs_id"]
        """Parent Unique Table ID"""
        self.proj_id: str = data["proj_id"]
        """Foreign Key for `PROJECT` WBS node belongs to"""
        self.seq_num: int | None = optional_int(data["seq_num"])
        """Sort Order"""
        self.status_code: str = data["status_code"]

        self.assignments: int = 0
        """Activity Assignment Count"""
        self.user_defined_fields: dict[UDFTYPE, Any] = {}

    def __eq__(self, __o: "PROJWBS") -> bool:
        return self.full_code == __o.full_code

    def __gt__(self, __o: "PROJWBS") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "PROJWBS") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash(self.full_code)

    def __str__(self) -> str:
        return f"{self.full_code} - {self.name}"

    @property
    def lineage(self) -> list["PROJWBS"]:
        if self.is_proj_node:
            return []

        if not self._parent:
            return [self]

        return self._parent.lineage + [self]

    @property
    def full_code(self) -> str:
        return ".".join(reversed([node.code for node in self.lineage]))
