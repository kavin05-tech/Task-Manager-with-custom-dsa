"""Application service layer coordinating persistence and algorithms."""

from __future__ import annotations

from dataclasses import replace
from typing import Optional

from data_structures.binary_search import binary_search, prefix_search
from data_structures.linked_list import LinkedList
from data_structures.queue import Queue
from data_structures.selection_sort import selection_sort
from data_structures.stack import Stack
from database import DatabaseManager
from models import Activity, Task, UndoAction
from utils import PRIORITY_VALUES, STATUSES, now_text, today_text, validate_task


class TaskManager:
    """Business rules for the Task Manager MVC application."""

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database
        self.undo_stack: Stack[UndoAction] = Stack()
        self.activity_log: LinkedList[Activity] = LinkedList()

    def _log(self, action: str, task: Task) -> None:
        self.activity_log.append(Activity(now_text(), action, task.title))

    def create_task(self, title: str, description: str, priority_name: str,
                    deadline: str, status: str = "Pending") -> Task:
        """Validate and create a task."""
        validate_task(title, deadline)
        if priority_name not in PRIORITY_VALUES or status not in STATUSES:
            raise ValueError("Invalid priority or status.")
        task = Task(None, title.strip(), description.strip(), PRIORITY_VALUES[priority_name],
                    status, now_text(), deadline)
        task = self.database.create_task(task)
        self._log("Task Created", task)
        return task

    def update_task(self, task_id: int, title: str, description: str,
                    priority_name: str, deadline: str, status: str) -> Task:
        """Store an undo snapshot, then update a task."""
        validate_task(title, deadline)
        previous = self._required(task_id)
        self.undo_stack.push(UndoAction("update", replace(previous)))
        previous.title, previous.description = title.strip(), description.strip()
        previous.priority, previous.deadline, previous.status = (
            PRIORITY_VALUES[priority_name], deadline, status)
        self.database.update_task(previous)
        self._log("Task Updated", previous)
        if status == "Completed":
            self._log("Task Completed", previous)
        return previous

    def delete_task(self, task_id: int) -> None:
        """Delete a task after retaining it on the custom undo stack."""
        task = self._required(task_id)
        self.undo_stack.push(UndoAction("delete", replace(task)))
        self.database.delete_task(task_id)
        self._log("Task Deleted", task)

    def undo(self) -> Optional[Task]:
        """Restore the most recently updated or deleted task."""
        if self.undo_stack.is_empty():
            return None
        action = self.undo_stack.pop()
        self.database.restore_task(action.task)
        self._log("Task Restored", action.task)
        return action.task

    def get_tasks(self, status: str = "All", sort_by: str = "Creation Date") -> list[Task]:
        """Return tasks after refreshing overdue state and requested ordering."""
        self.database.refresh_overdue(today_text())
        tasks = self.database.get_tasks(status)
        if sort_by == "Priority":
            return selection_sort(tasks, key=lambda task: task.priority, reverse=True)
        if sort_by == "Task Name":
            return selection_sort(tasks, key=lambda task: task.title.casefold())
        if sort_by == "Deadline":
            return selection_sort(tasks, key=lambda task: task.deadline or "9999-12-31")
        return tasks

    def search_tasks(self, phrase: str, status: str = "All") -> list[Task]:
        """Search title prefixes with binary search; retain substring convenience."""
        tasks = self.get_tasks(status, "Task Name")
        phrase = phrase.strip()
        if not phrase:
            return tasks
        exact = binary_search(tasks, phrase, key=lambda task: task.title)
        if exact:
            return [exact]
        prefix_matches = prefix_search(tasks, phrase, key=lambda task: task.title)
        if prefix_matches:
            return prefix_matches
        return [task for task in tasks if phrase.casefold() in task.title.casefold()]

    def process_next_task(self) -> Optional[Task]:
        """Build a FIFO custom queue of pending work and start its oldest task."""
        queue: Queue[Task] = Queue()
        for task in self.database.get_tasks("Pending"):
            queue.enqueue(task)
        if queue.is_empty():
            return None
        task = queue.dequeue()
        task.status = "In Progress"
        self.database.update_task(task)
        self._log("Task Processing Started", task)
        return task

    def dashboard(self) -> dict[str, int]:
        """Return dashboard metric values."""
        self.database.refresh_overdue(today_text())
        counts = self.database.count_by_status()
        counts["Total"] = sum(counts.values())
        return counts

    def activities(self) -> list[Activity]:
        """Materialize the activity linked list for display."""
        return list(self.activity_log)

    def _required(self, task_id: int) -> Task:
        task = self.database.get_task(task_id)
        if task is None:
            raise ValueError("The selected task no longer exists.")
        return task
