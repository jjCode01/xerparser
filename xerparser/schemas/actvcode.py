# xerparser
# actvcode.py

from functools import cached_property

from xerparser.schemas._node import Node
from xerparser.schemas.actvtype import ACTVTYPE


class ACTVCODE(Node):
    """
    A class to represent an Activity Code Value
    """

    def __init__(self, code_type: ACTVTYPE, **data: str) -> None:
        super().__init__()
        self.uid: str = data["actv_code_id"]
        """Unique Table ID"""
        self.actv_code_type_id: str = data["actv_code_type_id"]
        """Foreign Key to Activity Code Type"""
        self.code: str = data["short_name"]
        """Activity Code ID"""
        self.description: str = data["actv_code_name"]
        """Activity Code Description"""
        self.parent_actv_code_id: str = data["parent_actv_code_id"]
        """Parent Unique Table ID"""
        self.seq_num: int = int(data["seq_num"])
        """Sort Order"""
        self.code_type: ACTVTYPE = self._valid_actvtype(code_type)
        """Activity Code Type"""

    def __eq__(self, __o: "ACTVCODE") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __gt__(self, __o: "ACTVCODE") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "ACTVCODE") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    @cached_property
    def full_code(self) -> str:
        """Activity code including parent codes"""
        if not self.parent:
            return self.code

        return f"{self.parent.full_code}.{self.code}"

    def _valid_actvtype(self, value: ACTVTYPE) -> ACTVTYPE:
        """Validate Activity Code Type"""
        if not isinstance(value, ACTVTYPE):
            raise TypeError(f"Expected <class ACTVTYPE>; got {type(value)}")
        if value.uid != self.actv_code_type_id:
            raise ValueError(
                f"{value.uid} does not match act_code_type_id {self.actv_code_type_id}"
            )
        return value
