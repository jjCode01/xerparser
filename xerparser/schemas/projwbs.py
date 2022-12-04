from typing import Iterator
from pydantic import BaseModel


class WbsNode(BaseModel):
    """A class to represent a schedule WBS node."""

    wbs_id: str
    proj_id: str
    seq_num: int | None
    proj_node_flag: str
    status_code: str
    wbs_short_name: str
    wbs_name: str
    parent_wbs_id: str
    assignments: int = 0
    parent: "WbsNode" = None

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, __o: "WbsNode") -> bool:
        self_path = WbsLinkedList(self)
        other_path = WbsLinkedList(__o)
        return self_path.short_name_path(False) == other_path.short_name_path(False)

    def __hash__(self) -> int:
        self_path = WbsLinkedList(self)
        return hash(self_path.short_name_path(False))

    @property
    def is_project_node(self) -> bool:
        return self.proj_node_flag == "Y"


class WbsLinkedList:
    def __init__(self, tail: WbsNode = None) -> None:
        self.tail = tail

    def __eq__(self, __o: "WbsLinkedList") -> bool:
        return self.short_name_path() == __o.short_name_path()

    def __hash__(self) -> int:
        return hash(self.short_name_path())

    def iter_path(self, include_proj_node=False) -> Iterator[WbsNode]:
        node = self.tail
        if not include_proj_node and node.is_project_node:
            node = None

        while node is not None and not node.is_project_node:
            yield node
            node = node.parent

    def short_name_path(self, include_proj_node=False) -> str:
        short_path = ".".join(
            reversed(
                [node.wbs_short_name for node in self.iter_path(include_proj_node)]
            )
        )
        return short_path

    def long_name_path(self, include_proj_node=False) -> str:
        long_path = ".".join(
            reversed([node.wbs_name for node in self.iter_path(include_proj_node)])
        )
        return long_path
