# xerparser
# memotype.py


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

    def __init__(self, **data) -> None:
        self.uid: str = data["memo_type_id"]
        self.topic: str = data["memo_type"]

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
