"""Singly linked list used as the in-memory activity ledger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar


T = TypeVar("T")


@dataclass
class _ListNode(Generic[T]):
    value: T
    next: Optional["_ListNode[T]"] = None


class LinkedList(Generic[T]):
    """A simple append-only singly linked list."""

    def __init__(self) -> None:
        self._head: Optional[_ListNode[T]] = None
        self._tail: Optional[_ListNode[T]] = None
        self._size = 0

    def append(self, value: T) -> None:
        """Add a value to the end of the list."""
        node = _ListNode(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def __len__(self) -> int:
        return self._size
