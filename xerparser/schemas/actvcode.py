# xerparser
# actvcode.py

from typing import Optional

from xerparser.schemas.actvtype import ACTVTYPE


class ACTVCODE:
    """A class to represent an Activity Code Value"""

    def __init__(self, code_type: ACTVTYPE, **data) -> None:
        self.uid: str = data["actv_code_id"]
        self.actv_code_type_id: str = data["actv_code_type_id"]
        self.code: str = data["short_name"]
        self.description: str = data["actv_code_name"]
        self.parent_actv_code_id: str = data["parent_actv_code_id"]
        self.seq_num: int = int(data["seq_num"])
        self.code_type: ACTVTYPE = valid_actvtype(code_type)
        self._parent: "ACTVCODE" | None = None

    def __eq__(self, __o: "ACTVCODE") -> bool:
        return self.code == __o.code and self.code_type == __o.code_type

    def __gt__(self, __o: "ACTVCODE") -> bool:
        return self.code > __o.code

    def __lt__(self, __o: "ACTVCODE") -> bool:
        return self.code < __o.code

    def __hash__(self) -> int:
        return hash((self.code, self.code_type))

    @property
    def parent(self) -> Optional["ACTVCODE"]:
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

            self._parent = value


def valid_actvtype(value: ACTVTYPE) -> ACTVTYPE:
    if not isinstance(value, ACTVTYPE):
        raise ValueError(f"ValueError: expected <class ACTVTYPE>; got {type(value)}")
    return value
