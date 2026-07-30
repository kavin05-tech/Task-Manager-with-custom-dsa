"""A linked-node LIFO stack implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass
class _StackNode(Generic[T]):
    value: T
    next: Optional["_StackNode[T]"] = None


class Stack(Generic[T]):
    """A last-in-first-out stack built without using list storage."""

    def __init__(self) -> None:
        self._top: Optional[_StackNode[T]] = None
        self._size = 0

    def push(self, value: T) -> None:
        """Place *value* on the top of the stack."""
        self._top = _StackNode(value, self._top)
        self._size += 1

    def pop(self) -> T:
        """Remove and return the top value.

        Raises:
            IndexError: If the stack is empty.
        """
        if self._top is None:
            raise IndexError("pop from an empty stack")
        node = self._top
        self._top = node.next
        self._size -= 1
        return node.value

    def peek(self) -> T:
        """Return the top value without removing it."""
        if self._top is None:
            raise IndexError("peek from an empty stack")
        return self._top.value

    def is_empty(self) -> bool:
        """Return whether no values have been pushed."""
        return self._top is None

    def __len__(self) -> int:
        return self._size
