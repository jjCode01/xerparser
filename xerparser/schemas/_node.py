class Node:
    """A class to represent a node in a `Tree Data Structure`."""

    def __init__(self) -> None:
        self._parent = None
        self._children = []

    def addChild(self, child) -> None:
        if type(self) != type(child):
            raise TypeError(f"Expected {type(self)}; got {type(child)}")
        self._children.append(child)

    @property
    def children(self) -> list:
        return self._children

    @property
    def lineage(self) -> list:
        if not self._parent:
            return [self]

        return self._parent.lineage + [self]

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value) -> None:
        if value is None:
            return

        if type(self) != type(value):
            raise TypeError(f"Expected {type(self)}; got {type(value)}")

        self._parent = value
