"""SQLite persistence boundary for Task Manager."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from models import Task


class DatabaseManager:
    """Owns database creation and all task CRUD statements."""

    def __init__(self, path: str | Path = "task_manager.db") -> None:
        self.path = str(path)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS Tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deadline TEXT NOT NULL DEFAULT ''
                )
                """
            )

    @staticmethod
    def _task(row: sqlite3.Row) -> Task:
        return Task(**dict(row))

    def create_task(self, task: Task) -> Task:
        """Insert a new task and return it with its generated identifier."""
        with self._connect() as connection:
            cursor = connection.execute(
                """INSERT INTO Tasks (title, description, priority, status, created_at, deadline)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (task.title, task.description, task.priority, task.status,
                 task.created_at, task.deadline),
            )
        task.id = cursor.lastrowid
        return task

    def restore_task(self, task: Task) -> None:
        """Restore an exact task snapshot, preserving its original id."""
        with self._connect() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO Tasks
                   (id, title, description, priority, status, created_at, deadline)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (task.id, task.title, task.description, task.priority,
                 task.status, task.created_at, task.deadline),
            )

    def update_task(self, task: Task) -> None:
        """Persist all mutable fields for an existing task."""
        if task.id is None:
            raise ValueError("A task must have an id before it can be updated")
        with self._connect() as connection:
            connection.execute(
                """UPDATE Tasks SET title=?, description=?, priority=?, status=?, deadline=?
                   WHERE id=?""",
                (task.title, task.description, task.priority, task.status,
                 task.deadline, task.id),
            )

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id."""
        with self._connect() as connection:
            connection.execute("DELETE FROM Tasks WHERE id=?", (task_id,))

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve one task or None."""
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM Tasks WHERE id=?", (task_id,)).fetchone()
        return self._task(row) if row else None

    def get_tasks(self, status: str = "All") -> list[Task]:
        """Return all tasks, optionally restricted to one stored status."""
        statement, values = "SELECT * FROM Tasks", ()
        if status != "All":
            statement += " WHERE status=?"
            values = (status,)
        statement += " ORDER BY created_at ASC, id ASC"
        with self._connect() as connection:
            rows = connection.execute(statement, values).fetchall()
        return [self._task(row) for row in rows]

    def refresh_overdue(self, today: str) -> None:
        """Mark unfinished tasks whose deadline is before today as overdue."""
        with self._connect() as connection:
            connection.execute(
                """UPDATE Tasks SET status='Overdue'
                   WHERE status IN ('Pending', 'In Progress')
                   AND deadline <> '' AND deadline < ?""",
                (today,),
            )

    def count_by_status(self) -> dict[str, int]:
        """Return counts keyed by status."""
        counts = {"Pending": 0, "In Progress": 0, "Completed": 0, "Overdue": 0}
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM Tasks GROUP BY status"
            ).fetchall()
        for row in rows:
            counts[row["status"]] = row["count"]
        return counts
