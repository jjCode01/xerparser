# xerparser
# projwbs.py

from typing import Iterator
from pydantic import BaseModel, Field, validator


class PROJWBS(BaseModel):
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

    uid: str = Field(alias="wbs_id")
    assignments: int = 0
    code: str = Field(alias="wbs_short_name")
    is_proj_node: bool = Field(alias="proj_node_flag")
    name: str = Field(alias="wbs_name")
    parent: "PROJWBS" = None
    parent_wbs_id: str
    proj_id: str
    seq_num: int | None
    status_code: str

    class Config:
        arbitrary_types_allowed = True

    @validator("is_proj_node", pre=True)
    def flag_to_bool(cls, value):
        return value == "Y"

    @validator("seq_num", pre=True)
    def empty_str_to_none(cls, value):
        return (value, None)[value == ""]

    def __eq__(self, __o: "PROJWBS") -> bool:
        self_path = WbsLinkedList(self)
        other_path = WbsLinkedList(__o)
        return self_path.code_path(False) == other_path.code_path(False)

    def __hash__(self) -> int:
        self_path = WbsLinkedList(self)
        return hash(self_path.code_path(False))


class WbsLinkedList:
    """
    A class representing a linked list of WBS nodes.

    ...

    Attributes
    ----------
    tail: PROJWBS
        Last WBS Node in linked list


    Methods
    ----------
    code_path(include_proj_node: bool=False) -> Iterator[PROJWBS]
    iter_path(include_proj_node: bool=False) -> str
    name_path(include_proj_node: bool=False) -> str

    """

    def __init__(self, tail: PROJWBS = None) -> None:
        self.tail = tail

    def __eq__(self, __o: "WbsLinkedList") -> bool:
        return self.short_name_path() == __o.short_name_path()

    def __hash__(self) -> int:
        return hash(self.short_name_path())

    def iter_path(self, include_proj_node=False) -> Iterator[PROJWBS]:
        """Iterates through linked list from tail to head.

        Args:
            include_proj_node (bool, optional): Include Project Node as Head. Defaults to False.

        Yields:
            Iterator[PROJWBS]: WBS Node
        """
        node = self.tail
        if not include_proj_node and node.is_project_node:
            node = None

        while node is not None and not node.is_project_node:
            yield node
            node = node.parent

    def code_path(self, include_proj_node=False) -> str:
        """Generate full path of WBS Codes from head to tail seperated by a dot

        Args:
            include_proj_node (bool, optional): Include Project Node as Head. Defaults to False.

        Returns:
            str: Full path of WBS Codes from head to tail
        """
        short_path = ".".join(
            reversed([node.code for node in self.iter_path(include_proj_node)])
        )
        return short_path

    def name_path(self, include_proj_node=False) -> str:
        long_path = ".".join(
            reversed([node.name for node in self.iter_path(include_proj_node)])
        )
        return long_path
