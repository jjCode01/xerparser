# xerparser
# memotype.py

from typing import Any


class MEMOTYPE:
    """
    A class to represent a notebook topic.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [memo_type_id]
    topic: str
        Notebook Topic [memo_type]
    """

    def __init__(self, **data: Any) -> None:
        self.uid: str = data["memo_type_id"]
        self.topic: str = data["memo_type"]

    def __eq__(self, __o: "MEMOTYPE") -> bool:
        return self.topic == __o.topic

    def __hash__(self) -> int:
        return hash(self.topic)
