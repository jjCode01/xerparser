# xerparser
# pcatval.py

from functools import cached_property

from xerparser.schemas._node import Node
from xerparser.schemas.pcattype import PCATTYPE


class PCATVAL(Node):
    """
    A class to represent an Project Code Value
    """

    def __init__(self, code_type: PCATTYPE, **data: str) -> None:
        super().__init__()
        self.uid: str = data["proj_catg_id"]
        """Unique Table ID"""
        self.proj_catg_type_id: str = data["proj_catg_type_id"]
        """Foreign Key for Project Code Type `PCATTYPE`"""
        self.code: str = data["proj_catg_short_name"]
        """Project Code / Short Name"""
        self.description: str = data["proj_catg_name"]
        """Project Code Description"""
        self.parent_proj_catg_id: str = data["parent_proj_catg_id"]
        """Unique Table ID for Parent Code"""
        self.seq_num: int = int(data["seq_num"])
        """Sort Order"""
        self.code_type: PCATTYPE = self._valid_pcattype(code_type)
        """Project Code Type"""

    def __eq__(self, __o: "PCATVAL") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __gt__(self, __o: "PCATVAL") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "PCATVAL") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    @cached_property
    def full_code(self) -> str:
        """Project code including parent codes"""
        if not self.parent:
            return self.code

        return f"{self.parent.full_code}.{self.code}"

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
