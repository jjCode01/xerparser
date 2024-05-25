from typing import Self


class Node:
    """A class to represent a node in a `Tree Data Structure`."""

    def __init__(self, uid: str, code: str, name: str, parent_id: str) -> None:
        self.uid: str = uid
        """Unique Table ID"""
        self.code: str = code
        """Code or ID for Node"""
        self.name: str = name
        """Name or description of Node"""
        self.parent_id: str = parent_id
        """Parent Unique Table ID"""
        self._parent: Self | None = None
        self._children: list[Self] = []

    def __eq__(self, __o: Self) -> bool:
        self._validate(__o)
        return self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash(self.full_code)

    def __gt__(self, __o: Self) -> bool:
        return self.full_code > self._validate(__o).full_code

    def __lt__(self, __o: Self) -> bool:
        return self.full_code < self._validate(__o).full_code

    def __str__(self) -> str:
        return f"{self.full_code} - {self.name}"

    def addChild(self, child: Self) -> None:
        """Add child node"""
        self._children.append(self._validate(child))

    @property
    def children(self) -> list[Self]:
        """List of children nodes"""
        return self._children

    @property
    def full_code(self) -> str:
        """Cost code including parent codes"""
        if not self.parent:
            return self.code
        return f"{self.parent.full_code}.{self.code}"

    @property
    def lineage(self) -> list[Self]:
        if not self._parent:
            return [self]
        return self._parent.lineage + [self]

    @property
    def parent(self) -> Self | None:
        """Parent node"""
        return self._parent

    @parent.setter
    def parent(self, value: Self | None) -> None:
        if value is None:
            return
        self._parent = self._validate(value)

    def _validate(self, _o2) -> Self:
        if type(self) != type(_o2):
            raise TypeError(f"Expected {type(self)}; got {type(_o2)}")
        return _o2


def build_tree(nodes: dict[str, Node]) -> dict[str, Node]:
    for node in nodes.values():
        if parent := nodes.get(node.parent_id):
            node.parent = parent
            parent.addChild(node)
    return nodes
