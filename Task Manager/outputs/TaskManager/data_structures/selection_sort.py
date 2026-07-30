"""Manual selection-sort implementation used for priority ordering."""

from __future__ import annotations

from typing import Callable, TypeVar


T = TypeVar("T")


def selection_sort(items: list[T], key: Callable[[T], object], reverse: bool = False) -> list[T]:
    """Return a selection-sorted copy of *items* without calling sorted()."""
    result = items[:]
    for start in range(len(result)):
        selected = start
        for candidate in range(start + 1, len(result)):
            left, right = key(result[candidate]), key(result[selected])
            if (left > right) if reverse else (left < right):
                selected = candidate
        if selected != start:
            result[start], result[selected] = result[selected], result[start]
    return result
