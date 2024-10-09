# xerparser
# pcatval.py


from xerparser.schemas._node import Node
from xerparser.schemas.pcattype import PCATTYPE
from xerparser.src.validators import int_or_zero


class PCATVAL(Node):
    """
    A class to represent an Project Code Value
    """

    def __init__(self, code_type: PCATTYPE, **data: str) -> None:
        super().__init__(
            data["proj_catg_id"],
            data["proj_catg_short_name"],
            data["proj_catg_name"],
            data["parent_proj_catg_id"],
            int_or_zero(data["seq_num"]),
        )
        self.proj_catg_type_id: str = data["proj_catg_type_id"]
        """Foreign Key for Project Code Type `PCATTYPE`"""
        self.code_type: PCATTYPE = self._valid_pcattype(code_type)
        """Project Code Type"""

    def __eq__(self, __o: "PCATVAL") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    def _valid_pcattype(self, value: PCATTYPE) -> PCATTYPE:
        """Validate Activity Code Type"""
        if not isinstance(value, PCATTYPE):
            raise ValueError(
                f"ValueError: expected <class PCATTYPE>; got {type(value)}"
            )
        if value.uid != self.proj_catg_type_id:
            raise ValueError(
                f"ValueError: Unique ID {value.uid} does not match proj_catg_type_id {self.proj_catg_type_id}"  # noqa: E501
            )
        return value
