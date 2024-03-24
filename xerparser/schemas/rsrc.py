# xerparser
# rsrc.py

from typing import Any

from xerparser.schemas._node import Node
from xerparser.schemas.udftype import UDFTYPE


class RSRC(Node):
    """
    A class to represent a Resource.
    """

    def __init__(self, **data: str) -> None:
        super().__init__()
        self.uid: str = data["rsrc_id"]
        self.clndr_id: str = data["clndr_id"]
        self.name: str = data["rsrc_name"]
        self.parent_rsrc_id: str = data["parent_rsrc_id"]
        self.short_name: str = data["rsrc_short_name"]
        self.type: str = data["rsrc_type"]
        self.user_defined_fields: dict[UDFTYPE, Any] = {}

    def __eq__(self, __o: "RSRC") -> bool:
        self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash(self.full_code)

    @property
    def full_code(self) -> str:
        return ".".join(reversed([node.short_name for node in self.lineage]))
