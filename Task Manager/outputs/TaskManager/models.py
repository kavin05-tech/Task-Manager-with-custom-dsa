"""Domain objects used by the Task Manager application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Task:
    """A task persisted in SQLite and rendered by the user interface."""

    id: Optional[int]
    title: str
    description: str
    priority: int
    status: str
    created_at: str
    deadline: str

    @property
    def priority_name(self) -> str:
        """Return a readable priority label."""
        return {3: "High", 2: "Medium", 1: "Low"}.get(self.priority, "Low")


@dataclass(slots=True)
class Activity:
    """An activity entry stored in the custom linked list."""

    timestamp: str
    action: str
    task_name: str


@dataclass(slots=True)
class UndoAction:
    """Represents an operation that can restore a task's prior state."""

    operation: str
    task: Task
