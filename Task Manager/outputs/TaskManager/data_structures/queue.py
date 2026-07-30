"""A linked-node FIFO queue implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass
class _QueueNode(Generic[T]):
    value: T
    next: Optional["_QueueNode[T]"] = None


class Queue(Generic[T]):
    """A first-in-first-out queue with O(1) enqueue and dequeue."""

    def __init__(self) -> None:
        self._front: Optional[_QueueNode[T]] = None
        self._rear: Optional[_QueueNode[T]] = None
        self._size = 0

    def enqueue(self, value: T) -> None:
        """Append *value* to the rear of the queue."""
        node = _QueueNode(value)
        if self._rear is None:
            self._front = self._rear = node
        else:
            self._rear.next = node
            self._rear = node
        self._size += 1

    def dequeue(self) -> T:
        """Remove and return the front item."""
        if self._front is None:
            raise IndexError("dequeue from an empty queue")
        node = self._front
        self._front = node.next
        if self._front is None:
            self._rear = None
        self._size -= 1
        return node.value

    def front(self) -> T:
        """Return the next item without removing it."""
        if self._front is None:
            raise IndexError("front from an empty queue")
        return self._front.value

    def is_empty(self) -> bool:
        """Return whether this queue has no items."""
        return self._front is None

    def __len__(self) -> int:
        return self._size
