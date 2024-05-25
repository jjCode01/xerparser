# xerparser
# account.py

from xerparser.schemas._node import Node
from xerparser.src.validators import optional_int


class ACCOUNT(Node):
    """
    A class to represent a cost account.
    """

    def __init__(self, **data: str) -> None:
        super().__init__(
            data["acct_id"],
            data["acct_short_name"],
            data["acct_name"],
            data["parent_acct_id"],
        )
        self.description: str = _check_description(data["acct_descr"])
        """Cost Account Description"""
        self.seq_num: int | None = optional_int(data["acct_seq_num"])
        """Sort Order"""

    def __eq__(self, __o: "ACCOUNT") -> bool:
        if __o is None:
            return False
        return self.name == __o.name and self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash((self.name, self.full_code))


def _check_description(value: str) -> str:
    return (value, "")[value == "" or value == "ï»¿"]
