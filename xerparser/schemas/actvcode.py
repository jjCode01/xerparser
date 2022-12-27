# xerparser
# actvcode.py

from typing import Any

from xerparser.schemas.actvtype import ACTVTYPE


class ACTVCODE:
    """A class to represent an Activity Code Value"""

    def __init__(self, code_type: ACTVTYPE, **kwargs: Any) -> None:
        self.uid: str = kwargs["actv_code_id"]
        self.actv_code_type_id: str = kwargs["actv_code_type_id"]
        self.code: str = kwargs["short_name"]
        self.description: str = kwargs["actv_code_name"]
        self.parent_actv_code_id: str = kwargs["parent_actv_code_id"]
        self.seq_num: int = int(kwargs["seq_num"])
        self.parent: "ACTVCODE" | None = None
        self.code_type: ACTVTYPE = code_type

    def __eq__(self, __o: "ACTVCODE") -> bool:
        return self.code == __o.code and self.code_type == __o.code_type

    def __hash__(self) -> int:
        return hash((self.code, self.code_type))
