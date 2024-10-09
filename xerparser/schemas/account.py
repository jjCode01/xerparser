# xerparser
# account.py

from typing import Self

from xerparser.schemas._node import Node
from xerparser.src.validators import int_or_zero


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
            int_or_zero(data["acct_seq_num"]),
        )
        self.description: str = _check_description(data["acct_descr"])
        """Cost Account Description"""

    def __eq__(self, __o: Self) -> bool:
        if __o is None:
            return False
        return self.name == __o.name and self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash((self.name, self.full_code))


def _check_description(value: str) -> str:
    return (value, "")[value == "" or value == "ï»¿"]
