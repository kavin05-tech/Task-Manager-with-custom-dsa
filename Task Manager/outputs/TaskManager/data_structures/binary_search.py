"""Manual binary-search helpers for alphabetically ordered tasks."""

from __future__ import annotations

from typing import Callable, Optional, Sequence, TypeVar


T = TypeVar("T")


def binary_search(items: Sequence[T], target: str, key: Callable[[T], str]) -> Optional[T]:
    """Find an exact case-insensitive title match in an ordered sequence."""
    low, high = 0, len(items) - 1
    target = target.casefold()
    while low <= high:
        middle = (low + high) // 2
        value = key(items[middle]).casefold()
        if value == target:
            return items[middle]
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return None


def prefix_search(items: Sequence[T], prefix: str, key: Callable[[T], str]) -> list[T]:
    """Locate title-prefix matches using a manual lower-bound binary search."""
    prefix = prefix.casefold()
    low, high = 0, len(items)
    while low < high:
        middle = (low + high) // 2
        if key(items[middle]).casefold() < prefix:
            low = middle + 1
        else:
            high = middle
    matches: list[T] = []
    while low < len(items) and key(items[low]).casefold().startswith(prefix):
        matches.append(items[low])
        low += 1
    return matches
