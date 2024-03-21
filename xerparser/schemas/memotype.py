# xerparser
# memotype.py


class MEMOTYPE:
    """
    A class to represent a notebook topic.
    """

    def __init__(self, **data: str) -> None:
        self.uid: str = data["memo_type_id"]
        """Unique Table ID"""
        self.topic: str = data["memo_type"]
        """Notebook Topic"""

    def __eq__(self, __o: "MEMOTYPE") -> bool:
        return self.topic == __o.topic

    def __gt__(self, __o: "MEMOTYPE") -> bool:
        return self.topic > __o.topic

    def __lt__(self, __o: "MEMOTYPE") -> bool:
        return self.topic < __o.topic

    def __hash__(self) -> int:
        return hash(self.topic)

    def __str__(self) -> str:
        return self.topic
