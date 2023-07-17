# xerparser
# account.py

from xerparser.src.validators import int_or_none, str_or_none
from typing import Optional
from xerparser.src.errors import InvalidParent


class ACCOUNT:
    """
    A class to represent a cost account.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [acct_id]
    code: str
        Cost Account ID or Cost Code [acct_short_name]
    description: str
        Cost Account Description [acct_desc]
    name: str
        Cost Account Name [acct_name]
    parent_acct_id: str | None
        Parent Cost Account Unique ID
    seq_num: int | None
        Sequence Number for sorting [acct_seq_num]
    parent: ACCOUNT | None
        Cost Account Parent
    """

    def __init__(self, **data) -> None:
        self.uid: str = data["acct_id"]
        self.code: str = data["acct_short_name"]
        self.description: str = _check_description(data["acct_descr"])
        self.name: str = data["acct_name"]
        self.parent_acct_id: str | None = str_or_none(data["parent_acct_id"])
        self.seq_num: int | None = int_or_none(data["acct_seq_num"])
        self._parent: Optional["ACCOUNT"] = None
        self._children: list["ACCOUNT"] = []

    def __eq__(self, __o: "ACCOUNT") -> bool:
        return self.name == __o.name and self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash((self.name, self.full_code))

    def __gt__(self, __o: "ACCOUNT") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "ACCOUNT") -> bool:
        return self.full_code < __o.full_code

    def __str__(self) -> str:
        return f"{self.full_code} - {self.name}"

    def addChild(self, child: "ACCOUNT") -> None:
        if not isinstance(child, ACCOUNT):
            raise TypeError(f"Expected <class ACCOUNT>; got {type(child)}")

        self._children.append(child)

    @property
    def children(self) -> list["ACCOUNT"]:
        return self._children

    @property
    def full_code(self) -> str:
        """Cost code including parent codes"""
        if not self.parent:
            return self.code

        return f"{self.parent.full_code}.{self.code}"

    @property
    def parent(self) -> Optional["ACCOUNT"]:
        """Parent Cost Account"""
        return self._parent

    @parent.setter
    def parent(self, value: Optional["ACCOUNT"]) -> None:
        """Parent Cost Account"""
        if value is None:
            self._parent = None

        elif isinstance(value, ACCOUNT):
            if value.uid != self.parent_acct_id:
                raise InvalidParent(value.uid, self.parent_acct_id)
            self._parent = value

        else:
            raise TypeError(f"Expected <class ACCOUNT> for parent; got {type(value)}")


def _check_description(value: str) -> str:
    return (value, "")[value == "" or value == "ï»¿"]
