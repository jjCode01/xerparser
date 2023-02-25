# xerparser
# pcatval.py

from functools import cached_property
from typing import Optional

from xerparser.schemas.pcattype import PCATTYPE


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

    def __eq__(self, __o: "PCATVAL") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __gt__(self, __o: "PCATVAL") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "PCATVAL") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    @property
    def lineage(self) -> list["PCATVAL"]:
        path = []
        proj_code = self
        while proj_code:
            path.append(proj_code)
            proj_code = proj_code.parent

        return path

    @cached_property
    def full_code(self) -> str:
        return ".".join(reversed([proj_code.code for proj_code in self.lineage]))

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
                raise ValueError(
                    f"ValueError: expected <class PCATVAL> for parent, got {type(value)}."
                )
            if value.uid != self.parent_proj_catg_id:
                raise ValueError(
                    f"ValueError: Parent ID {value.uid} does not match parent_actv_code_id {self.parent_proj_catg_id}"
                )

            self._parent = value

    def _valid_pcattype(self, value: PCATTYPE) -> PCATTYPE:
        """Validate Activity Code Type"""
        if not isinstance(value, PCATTYPE):
            raise ValueError(
                f"ValueError: expected <class PCATTYPE>; got {type(value)}"
            )
        if value.uid != self.proj_catg_type_id:
            raise ValueError(
                f"ValueError: Unique ID {value.uid} does not match proj_catg_type_id {self.proj_catg_type_id}"
            )
        return value
