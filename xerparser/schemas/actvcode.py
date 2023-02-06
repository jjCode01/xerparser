# xerparser
# actvcode.py

from functools import cached_property
from typing import Optional

from xerparser.schemas.actvtype import ACTVTYPE


class ACTVCODE:
    """
    A class to represent an Activity Code Value

    ...

    Attributes
    ----------
    uid: str
        Unique ID [actv_code_id]
    actv_code_type_id: str
        Foreign key for ACTVTYPE
    code: str
        Activity Code Value [short_name]
    description: str
        Activity Code Description [actv_code_name]
    parent_actv_code_id: str
        Unique ID of Parent Activity Code Value [parent_actv_code_id]
    seq_num: int
        Sort Order
    code_type: ACTVTYPE
        Activity Code Type
    parent: ACTVCODE | None
        Parent Activity Code Value
    """

    def __init__(self, code_type: ACTVTYPE, **data) -> None:
        self.uid: str = data["actv_code_id"]
        self.actv_code_type_id: str = data["actv_code_type_id"]
        self.code: str = data["short_name"]
        self.description: str = data["actv_code_name"]
        self.parent_actv_code_id: str = data["parent_actv_code_id"]
        self.seq_num: int = int(data["seq_num"])
        self.code_type: ACTVTYPE = self._valid_actvtype(code_type)
        self._parent: "ACTVCODE" | None = None

    def __eq__(self, __o: "ACTVCODE") -> bool:
        return self.full_code == __o.full_code and self.code_type == __o.code_type

    def __gt__(self, __o: "ACTVCODE") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "ACTVCODE") -> bool:
        return self.full_code < __o.full_code

    def __hash__(self) -> int:
        return hash((self.full_code, self.code_type))

    @property
    def lineage(self) -> list["ACTVCODE"]:
        path = []
        actv_code = self
        while actv_code:
            path.append(actv_code)
            actv_code = actv_code.parent

        return path

    @cached_property
    def full_code(self) -> str:
        return ".".join(reversed([actv_code.code for actv_code in self.lineage]))

    @property
    def parent(self) -> Optional["ACTVCODE"]:
        """Parent Activity Code Value. Can be None."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional["ACTVCODE"]) -> None:
        if value is None:
            self._parent = None
        else:
            if not isinstance(value, ACTVCODE):
                raise ValueError(
                    f"ValueError: expected <class ACTVCODE> for parent, got {type(value)}."
                )
            if value.uid != self.parent_actv_code_id:
                raise ValueError(
                    f"ValueError: Parent ID {value.uid} does not match parent_actv_code_id {self.parent_actv_code_id}"
                )

            self._parent = value

    def _valid_actvtype(self, value: ACTVTYPE) -> ACTVTYPE:
        """Validate Activity Code Type"""
        if not isinstance(value, ACTVTYPE):
            raise ValueError(
                f"ValueError: expected <class ACTVTYPE>; got {type(value)}"
            )
        if value.uid != self.actv_code_type_id:
            raise ValueError(
                f"ValueError: Unique ID {value.uid} does not match act_code_type_id {self.actv_code_type_id}"
            )
        return value
