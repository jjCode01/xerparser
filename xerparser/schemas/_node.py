from typing import Iterator, Self


class Node:
    """A class to represent a node in a `Tree Data Structure`."""

    def __init__(
        self, uid: str, code: str, name: str, parent_id: str, seq_num: int = 0
    ) -> None:
        self.uid: str = uid
        """Unique Table ID"""
        self.code: str = code
        """Code or ID for Node"""
        self.name: str = name
        """Name or description of Node"""
        self.parent_id: str = parent_id
        """Parent Unique Table ID"""
        self.seq_num = seq_num
        self._parent: Self | None = None
        self._children: dict[str, Self] = {}

    def __eq__(self, __o: Self) -> bool:
        self._validate(__o)
        return self.full_code == __o.full_code

    def __hash__(self) -> int:
        return hash(self.full_code)

    def __gt__(self, __o: Self) -> bool:
        self._validate(__o)
        if self.parent == __o.parent:
            if self.seq_num != __o.seq_num:
                return self.seq_num > __o.seq_num
        return self.full_code > __o.full_code

    def __lt__(self, __o: Self) -> bool:
        self._validate(__o)
        if self.parent == __o.parent:
            if self.seq_num != __o.seq_num:
                return self.seq_num < __o.seq_num
        return self.full_code < __o.full_code

    def __str__(self) -> str:
        return f"{self.full_code} - {self.name}"

    def addChild(self, child: Self) -> None:
        """Add child node"""
        self._validate(child)
        self._children[child.uid] = child

    @property
    def children(self) -> list[Self]:
        """List of children nodes"""
        return list(self._children.values())

    @property
    def depth(self) -> int:
        """
        Length of the path to the root node (i.e., root path).
        Root node will have a depth of 0.
        """
        return len(self.lineage) - 1

    @property
    def height(self) -> int:
        """
        Length of the longest downward path to a leaf.
        Leaves will have a height of 0.
        """
        return max([child.depth for child in self.traverse_children()]) - self.depth

    @property
    def full_code(self) -> str:
        """Node code/ID including parent codes/IDs"""
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

    @property
    def size(self) -> int:
        """Number of children and decendent nodes"""
        return len([child for child in self.traverse_children()]) - 1

    def traverse_parents(self) -> Iterator[Self]:
        """Iterate through parents to root."""
        yield self
        if self.parent:
            yield from self.parent.traverse_parents()

    def traverse_children(self) -> Iterator[Self]:
        """Iterate through children to leaves."""
        yield self
        for child in self.children:
            yield from child.traverse_children()

    def _validate(self, _o2) -> Self:
        if type(self) is not type(_o2):
            raise TypeError(f"Expected {type(self)}; got {type(_o2)}")
        return _o2


def build_tree(nodes: dict[str, Node]) -> dict[str, Node]:
    for node in nodes.values():
        if parent := nodes.get(node.parent_id):
            node.parent = parent
            parent.addChild(node)
    return nodes
