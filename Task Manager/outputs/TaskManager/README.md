# Task Manager with Custom Data Structures

A desktop task-management application built with Python, Tkinter, and SQLite. It demonstrates clean object-oriented design and core data structures/algorithms implemented manually rather than delegated to library conveniences.

## Features

- Full SQLite-backed task CRUD: create, edit, delete, inspect, and restore tasks.
- Status tracking: Pending, In Progress, Completed, and automatic Overdue detection.
- High, Medium, and Low priorities; visual priority and status indicators.
- Search task titles with a manual binary search (exact and prefix matching).
- Sort by priority through a manual selection sort, plus deadline, name, and creation-date views.
- Undo edit/delete operations using a custom node-based stack.
- FIFO “Process Next Task” workflow using a custom node-based queue.
- Session activity log stored in a custom singly linked list.
- Dashboard metrics, completion progress bar, status filters, input validation, deletion confirmation, and dark mode.

## Project Structure

```text
TaskManager/
├── main.py                 # Application composition and startup
├── models.py               # Task, activity, and undo domain objects
├── database.py             # SQLite repository
├── controller.py           # Business rules / MVC controller
├── gui.py                  # Tkinter view layer
├── utils.py                # Validation and shared constants
├── data_structures/
│   ├── stack.py            # Custom linked-node Stack
│   ├── queue.py            # Custom linked-node Queue
│   ├── linked_list.py      # Custom singly LinkedList
│   ├── binary_search.py    # Manual binary search helpers
│   └── selection_sort.py   # Manual selection sort
└── assets/                 # Reserved for screenshots/icons
```

## Architecture

The project follows a lightweight MVC design:

- **Model**: `Task`, `Activity`, and `UndoAction` dataclasses in `models.py`.
- **View**: `TaskManagerGUI` and `TaskForm` render widgets and show dialogs. They do not contain SQL.
- **Controller**: `TaskManager` validates workflow rules, selects algorithms, manages undo/log state, and coordinates persistence.
- **Persistence**: `DatabaseManager` contains the SQLite schema and parameterized CRUD statements.

## Custom Data Structures

| Component | Implementation | Application use |
|---|---|---|
| Stack | Singly linked nodes; `push`, `pop`, `peek`, `is_empty` | Holds pre-edit and pre-delete snapshots for Undo |
| Queue | Front/rear linked nodes; `enqueue`, `dequeue`, `front`, `is_empty` | Processes oldest pending task first |
| Linked List | Append-only singly linked nodes | Stores time-stamped activity events |
| Binary Search | Iterative exact search and lower-bound prefix lookup | Searches an alphabetically ordered task list |
| Selection Sort | Explicit minimum/maximum selection swaps | Sorts task priority without `sorted()` |

## Installation

### Requirements

- Python 3.12 or later
- Tkinter (included with standard Windows/macOS Python installations)
- No third-party packages are required.

### Run

From this directory:

```powershell
cd TaskManager
python main.py
```

On first launch, `task_manager.db` is created alongside `main.py` automatically.

## How to Test Every Feature

1. Click **Add Task**. Create several tasks with different priorities and deadlines; leave one deadline empty to verify optional dates.
2. Use the **Status** and **Sort** dropdowns. Select **Priority** to exercise selection sort.
3. Enter the beginning of a task title and click **Search** to exercise the binary-search prefix lookup. Try an exact title too.
4. Double-click a row or choose **View Details**.
5. Edit a task, then press **Undo**; its previous snapshot should return. Delete another task, confirm the dialog, then press **Undo** to restore it.
6. Add two pending tasks at different times. Click **Process Next Task**; the oldest becomes **In Progress**, demonstrating FIFO queue behavior.
7. Edit a task to **Completed**, then inspect the green row and dashboard progress bar.
8. Give a non-completed task a past deadline and refresh/filter; it becomes **Overdue**.
9. Click **View Logs** to inspect events accumulated in the custom linked list for this session.
10. Toggle **Dark mode** to verify the alternate theme.

## Screenshots

Add screenshots to `assets/` when presenting the project:

- `assets/dashboard.png` — dashboard and task table
- `assets/task-form.png` — add/edit task form
- `assets/activity-log.png` — linked-list activity log window

## Future Improvements

- Persist activity history and undo history across sessions.
- Add recurring tasks, tags, attachments, and calendar views.
- Add unit tests with a temporary SQLite database.
- Support configurable reminder notifications and export/import.

## Resume Highlights

- Designed a modular Python desktop application using MVC, OOP, Tkinter, and SQLite.
- Implemented linked-node stack, queue, and singly linked-list structures from scratch and connected them to user-visible workflows.
- Implemented iterative binary search and selection sort manually to support task discovery and prioritization.
- Applied typed dataclasses, parameterized SQL, validation, error handling, and separation of concerns.
