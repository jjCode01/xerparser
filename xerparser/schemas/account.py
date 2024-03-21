# xerparser
# account.py

from xerparser.schemas._node import Node
from xerparser.src.validators import optional_int, optional_str


class ACCOUNT(Node):
    """
    A class to represent a cost account.
    """

    def __init__(self, **data: str) -> None:
        super().__init__()
        self.uid: str = data["acct_id"]
        """Unique Table ID"""
        self.code: str = data["acct_short_name"]
        """Cost Code / Account ID"""
        self.description: str = _check_description(data["acct_descr"])
        """Cost Account Description"""
        self.name: str = data["acct_name"]
        """Cost Account Name"""
        self.parent_acct_id: str | None = optional_str(data["parent_acct_id"])
        """Parent Unique Table ID"""
        self.seq_num: int | None = optional_int(data["acct_seq_num"])
        """Sort Order"""

    def __eq__(self, __o: "ACCOUNT") -> bool:
        if __o is None:
            return False
        return self.name == __o.name and self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash((self.name, self.full_code))

    def __gt__(self, __o: "ACCOUNT") -> bool:
        return self.full_code > __o.full_code

    def __lt__(self, __o: "ACCOUNT") -> bool:
        return self.full_code < __o.full_code

    def __str__(self) -> str:
        return f"{self.full_code} - {self.name}"

    @property
    def full_code(self) -> str:
        """Cost code including parent codes"""
        if not self.parent:
            return self.code

        return f"{self.parent.full_code}.{self.code}"


def _check_description(value: str) -> str:
    return (value, "")[value == "" or value == "ï»¿"]
