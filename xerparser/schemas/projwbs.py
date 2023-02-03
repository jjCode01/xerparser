# xerparser
# projwbs.py

from typing import Optional
from xerparser.src.validators import int_or_none


class PROJWBS:
    """
    A class to represent a schedule WBS node.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [wbs_id]
    assignments: int
        Activity Assignment Count
    code: str
        WBS Code [wbs_short_name]
    full_code: str
        WBS Codes from Head to Tail seperated by a dot
    is_proj_node: bool
        Project Node Flag
    name: str
        WBS Name [wbs_name]
    parent: PROJWBS | None
        Parent WBS Node
    parent_wbs_id: str
        Parent WBS Node Unique ID
    proj_id: str
        Project Unique ID
    seq_num: int | None
        Sort Order
    status_code: str
        Project Status

    """

    def __init__(self, **data) -> None:
        self.uid: str = data["wbs_id"]
        self.code: str = data["wbs_short_name"]
        self.is_proj_node: bool = data["proj_node_flag"] == "Y"
        self.name: str = data["wbs_name"]
        self.parent_wbs_id: str = data["parent_wbs_id"]
        self.proj_id: str = data["proj_id"]
        self.seq_num: int | None = int_or_none(data["seq_num"])
        self.status_code: str = data["status_code"]

        self.assignments: int = 0
        self._parent: Optional["PROJWBS"] = None

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

        path = []
        node = self
        while node and not node.is_proj_node:
            path.append(node)
            node = node.parent

        return path

    @property
    def full_code(self) -> str:
        return ".".join(reversed([node.code for node in self.lineage]))

    @property
    def parent(self) -> Optional["PROJWBS"]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional["PROJWBS"]) -> None:
        if value is None:
            self._parent = None
        else:
            if not isinstance(value, PROJWBS):
                raise ValueError(
                    f"ValueError: expected <class PROJWBS> for parent, got {type(value)}."
                )
            if value.uid != self.parent_wbs_id:
                raise ValueError(
                    f"ValueError: Parent Unique ID {value.uid} does not match {self.parent_wbs_id}"
                )

            self._parent = value
