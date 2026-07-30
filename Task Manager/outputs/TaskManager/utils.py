"""Small validation and presentation helpers."""

from __future__ import annotations

from datetime import date, datetime


PRIORITY_VALUES = {"Low": 1, "Medium": 2, "High": 3}
STATUSES = ("Pending", "In Progress", "Completed", "Overdue")


def now_text() -> str:
    """Return a sortable local timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text() -> str:
    """Return today's ISO date."""
    return date.today().isoformat()


def validate_task(title: str, deadline: str) -> None:
    """Validate mandatory title and optional ISO deadline."""
    if not title.strip():
        raise ValueError("Task title is required.")
    if len(title.strip()) > 120:
        raise ValueError("Task title must be 120 characters or fewer.")
    if deadline:
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("Deadline must use YYYY-MM-DD format.") from error
