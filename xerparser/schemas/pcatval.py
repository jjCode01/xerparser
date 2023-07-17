# xerparser
# pcatval.py

from functools import cached_property
from typing import Optional

from xerparser.schemas.pcattype import PCATTYPE
from xerparser.src.errors import InvalidParent


class PCATVAL:
    """
    A class to represent an Project Code Value

    ...

    Attributes
    ----------
    uid: str
        Unique ID [proj_catg_id]
    proj_catg_type_id: str
        Foreign key for PCATTYPE
    code: str
        Project Code Value [proj_catg_short_name]
    description: str
        Project Code Description [proj_catg_name]
    parent_proj_catg_id: str
        Unique ID of Parent Project Code Value
    seq_num: int
        Sort Order
    code_type: PCATTYPE
        Project Code Type
    parent: PCATVAL | None
        Parent Project Code Value
    """

    def __init__(self, code_type: PCATTYPE, **data) -> None:
        self.uid: str = data["proj_catg_id"]
        self.proj_catg_type_id: str = data["proj_catg_type_id"]
        self.code: str = data["proj_catg_short_name"]
        self.description: str = data["proj_catg_name"]
        self.parent_proj_catg_id: str = data["parent_proj_catg_id"]
        self.seq_num: int = int(data["seq_num"])
        self.code_type: PCATTYPE = self._valid_pcattype(code_type)
        self._parent: "PCATVAL" | None = None
        self._children: list["PCATVAL"] = []

    def __eq__(self, __o: "PCATVAL") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __gt__(self, __o: "PCATVAL") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "PCATVAL") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    def addChild(self, child: "PCATVAL") -> None:
        if not isinstance(child, PCATVAL):
            raise TypeError(f"Expected <class PCATVAL>; got {type(child)}")

        self._children.append(child)

    @property
    def children(self) -> list["PCATVAL"]:
        return self._children

    @property
    def lineage(self) -> list["PCATVAL"]:
        if not self.parent:
            return [self]

        return self.parent.lineage + [self]

    @cached_property
    def full_code(self) -> str:
        if not self.parent:
            return self.code

        return f"{self.parent.full_code}.{self.code}"

    @property
    def parent(self) -> Optional["PCATVAL"]:
        """Parent Project Code Value. Can be None."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional["PCATVAL"]) -> None:
        if value is None:
            self._parent = None
        else:
            if not isinstance(value, PCATVAL):
                raise TypeError(f"Expected <class PCATVAL>; got {type(value)}.")
            if value.uid != self.parent_proj_catg_id:
                raise InvalidParent(value.uid, self.parent_proj_catg_id)

            self._parent = value

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
