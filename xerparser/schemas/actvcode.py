# xerparser
# actvcode.py


from xerparser.schemas._node import Node
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.src.validators import int_or_zero


class ACTVCODE(Node):
    """
    A class to represent an Activity Code Value
    """

    def __init__(self, code_type: ACTVTYPE, **data: str) -> None:
        super().__init__(
            data["actv_code_id"],
            data["short_name"],
            data["actv_code_name"],
            data["parent_actv_code_id"],
            int_or_zero(data["seq_num"]),
        )
        self.actv_code_type_id: str = data["actv_code_type_id"]
        """Foreign Key to Activity Code Type"""
        self.code_type: ACTVTYPE = self._valid_actvtype(code_type)
        """Activity Code Type"""

    def __eq__(self, __o: "ACTVCODE") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    def _valid_actvtype(self, value: ACTVTYPE) -> ACTVTYPE:
        """Validate Activity Code Type"""
        if not isinstance(value, ACTVTYPE):
            raise TypeError(f"Expected <class ACTVTYPE>; got {type(value)}")
        if value.uid != self.actv_code_type_id:
            raise ValueError(
                f"{value.uid} does not match act_code_type_id {self.actv_code_type_id}"
            )
        return value
