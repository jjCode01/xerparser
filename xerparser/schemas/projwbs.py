# xerparser
# projwbs.py

from pydantic import BaseModel, Field, validator
from typing import Optional


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

    uid: str = Field(alias="wbs_id")
    assignments: int = 0
    code: str = Field(alias="wbs_short_name")
    is_proj_node: bool = Field(alias="proj_node_flag")
    name: str = Field(alias="wbs_name")
    parent: Optional["PROJWBS"] = None
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
        return self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash(self.full_code)

    @property
    def full_code(self) -> str:
        if self.is_proj_node:
            return ""

        path = []
        node = self
        while node and not node.is_proj_node:
            path.append(node.code)
            node = node.parent

        return ".".join(reversed(path))
