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
        super().__init__(
            data["rsrc_id"],
            data["rsrc_short_name"],
            data["rsrc_name"],
            data["parent_rsrc_id"],
        )
        self.clndr_id: str = data["clndr_id"]
        self.type: str = data["rsrc_type"]
        self.user_defined_fields: dict[UDFTYPE, Any] = {}
