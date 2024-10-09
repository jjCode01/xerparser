# xerparser
# rsrc.py

from typing import Any

from xerparser.schemas._node import Node
from xerparser.schemas.udftype import UDFTYPE
from xerparser.src.validators import int_or_zero


class RSRC(Node):
    """
    A class to represent a Resource.
    """

    def __init__(self, **data: str) -> None:
        from xerparser.schemas.taskrsrc import TASKRSRC

        super().__init__(
            data["rsrc_id"],
            data["rsrc_short_name"],
            data["rsrc_name"],
            data["parent_rsrc_id"],
            int_or_zero(data["rsrc_seq_num"]),
        )
        self.clndr_id: str = data["clndr_id"]
        self.type: str = data["rsrc_type"]
        self.user_defined_fields: dict[UDFTYPE, Any] = {}
        self.task_rsrcs: list[TASKRSRC] = []
