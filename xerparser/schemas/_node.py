from typing import Self


class Node:
    """A class to represent a node in a `Tree Data Structure`."""

    def __init__(self) -> None:
        self._parent: Self | None = None
        self._children: list[Self] = []

    def addChild(self, child: Self) -> None:
        """Add child node"""
        if type(self) != type(child):
            raise TypeError(f"Expected {type(self)}; got {type(child)}")
        self._children.append(child)

    @property
    def children(self) -> list[Self]:
        """List of children nodes"""
        return self._children

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

        if type(self) != type(value):
            raise TypeError(f"Expected {type(self)}; got {type(value)}")

        self._parent = value
