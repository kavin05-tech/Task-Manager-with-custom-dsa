"""Desktop application entry point."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

from controller import TaskManager
from database import DatabaseManager
from gui import TaskManagerGUI


def main() -> None:
    """Create the MVC collaborators and start Tk's event loop."""
    root = tk.Tk()
    database = DatabaseManager(Path(__file__).with_name("task_manager.db"))
    TaskManagerGUI(root, TaskManager(database))
    root.mainloop()


if __name__ == "__main__":
    main()
