"""Tkinter view layer for the Task Manager desktop application."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from controller import TaskManager
from models import Task
from utils import STATUSES


class TaskForm(tk.Toplevel):
    """Modal create/edit task form that delegates saving to a callback."""

    def __init__(self, parent: tk.Tk, on_save: Callable[..., None], task: Optional[Task] = None) -> None:
        super().__init__(parent)
        self.title("Edit Task" if task else "Add Task")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._on_save = on_save
        self._task = task
        self._build(task)

    def _build(self, task: Optional[Task]) -> None:
        frame = ttk.Frame(self, padding=18)
        frame.grid(sticky="nsew")
        ttk.Label(frame, text="Title *").grid(row=0, column=0, sticky="w", pady=4)
        self.title_var = tk.StringVar(value=task.title if task else "")
        ttk.Entry(frame, textvariable=self.title_var, width=46).grid(row=0, column=1, pady=4)
        ttk.Label(frame, text="Description").grid(row=1, column=0, sticky="nw", pady=4)
        self.description = tk.Text(frame, width=35, height=5, wrap="word")
        self.description.grid(row=1, column=1, pady=4)
        if task:
            self.description.insert("1.0", task.description)
        ttk.Label(frame, text="Priority").grid(row=2, column=0, sticky="w", pady=4)
        self.priority_var = tk.StringVar(value=task.priority_name if task else "Medium")
        ttk.Combobox(frame, textvariable=self.priority_var, values=("High", "Medium", "Low"),
                     state="readonly", width=18).grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="Status").grid(row=3, column=0, sticky="w", pady=4)
        self.status_var = tk.StringVar(value=task.status if task else "Pending")
        ttk.Combobox(frame, textvariable=self.status_var, values=STATUSES,
                     state="readonly", width=18).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="Deadline").grid(row=4, column=0, sticky="w", pady=4)
        self.deadline_var = tk.StringVar(value=task.deadline if task else "")
        ttk.Entry(frame, textvariable=self.deadline_var, width=22).grid(row=4, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="YYYY-MM-DD (optional)", style="Hint.TLabel").grid(
            row=5, column=1, sticky="w")
        ttk.Button(frame, text="Save Task", command=self._save).grid(
            row=6, column=1, sticky="e", pady=(14, 0))

    def _save(self) -> None:
        try:
            self._on_save(self.title_var.get(), self.description.get("1.0", "end-1c"),
                          self.priority_var.get(), self.deadline_var.get().strip(),
                          self.status_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid task", str(error), parent=self)
            return
        self.destroy()


class TaskManagerGUI:
    """Main application window and all Tkinter-specific behaviour."""

    def __init__(self, root: tk.Tk, controller: TaskManager) -> None:
        self.root, self.controller, self.dark_mode = root, controller, False
        self.search_var, self.status_var = tk.StringVar(), tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="Creation Date")
        self.metrics: dict[str, tk.StringVar] = {key: tk.StringVar(value="0") for key in
                                                  ("Total", "Completed", "Pending", "Overdue")}
        self._configure_window()
        self._build()
        self.refresh()

    def _configure_window(self) -> None:
        self.root.title("Task Manager • Custom Data Structures")
        self.root.geometry("1080x690")
        self.root.minsize(850, 560)
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("Hint.TLabel", foreground="#6b7280")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Metric.TLabel", font=("Segoe UI", 20, "bold"))

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)
        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="Task Manager", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Custom Data Structures", style="Hint.TLabel").pack(side="left", padx=12)
        ttk.Button(header, text="☾ Dark mode", command=self.toggle_theme).pack(side="right")
        dashboard = ttk.Frame(outer)
        dashboard.pack(fill="x", pady=(16, 12))
        for index, name in enumerate(("Total", "Completed", "Pending", "Overdue")):
            card = ttk.LabelFrame(dashboard, text=name, padding=10)
            card.grid(row=0, column=index, sticky="ew", padx=(0, 8))
            ttk.Label(card, textvariable=self.metrics[name], style="Metric.TLabel").pack()
            dashboard.columnconfigure(index, weight=1)
        self.progress = ttk.Progressbar(outer, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 14))
        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Entry(controls, textvariable=self.search_var, width=28).pack(side="left")
        ttk.Button(controls, text="Search", command=self.refresh).pack(side="left", padx=5)
        ttk.Label(controls, text="Status:").pack(side="left", padx=(12, 3))
        status = ttk.Combobox(controls, textvariable=self.status_var, values=("All",) + STATUSES,
                              state="readonly", width=13)
        status.pack(side="left")
        status.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        ttk.Label(controls, text="Sort:").pack(side="left", padx=(12, 3))
        sort = ttk.Combobox(controls, textvariable=self.sort_var,
                            values=("Creation Date", "Priority", "Deadline", "Task Name"),
                            state="readonly", width=15)
        sort.pack(side="left")
        sort.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        columns = ("id", "title", "priority", "status", "deadline", "created")
        self.table = ttk.Treeview(outer, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "title": "Task Name", "priority": "Priority", "status": "Status",
                    "deadline": "Deadline", "created": "Created"}
        widths = {"id": 55, "title": 330, "priority": 90, "status": 115, "deadline": 105, "created": 155}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], anchor="w")
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure("Completed", foreground="#16803c")
        self.table.tag_configure("In Progress", foreground="#9a6700")
        self.table.tag_configure("Pending", foreground="#6b7280")
        self.table.tag_configure("Overdue", foreground="#c02626")
        self.table.tag_configure("High", foreground="#dc2626")
        self.table.bind("<Double-1>", lambda _event: self.show_details())
        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(12, 0))
        for text, callback in (("Add Task", self.add_task), ("Edit Task", self.edit_task),
                               ("Delete Task", self.delete_task), ("Undo", self.undo),
                               ("Process Next Task", self.process_next), ("View Details", self.show_details),
                               ("View Logs", self.view_logs)):
            ttk.Button(actions, text=text, command=callback).pack(side="left", padx=(0, 7))

    def refresh(self) -> None:
        """Refresh task rows and dashboard values from the controller."""
        for item in self.table.get_children():
            self.table.delete(item)
        phrase = self.search_var.get().strip()
        tasks = (self.controller.search_tasks(phrase, self.status_var.get()) if phrase else
                 self.controller.get_tasks(self.status_var.get(), self.sort_var.get()))
        for task in tasks:
            tag = "High" if task.priority == 3 and task.status not in ("Completed", "Overdue") else task.status
            self.table.insert("", "end", values=(task.id, task.title, task.priority_name, task.status,
                              task.deadline or "—", task.created_at), tags=(tag,))
        metrics = self.controller.dashboard()
        for key, variable in self.metrics.items():
            variable.set(str(metrics[key]))
        self.progress["value"] = (metrics["Completed"] / metrics["Total"] * 100) if metrics["Total"] else 0

    def selected_id(self) -> Optional[int]:
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a task", "Select a task from the table first.", parent=self.root)
            return None
        return int(self.table.item(selection[0], "values")[0])

    def add_task(self) -> None:
        TaskForm(self.root, self._create_from_form)

    def _create_from_form(self, title: str, description: str, priority: str, deadline: str, status: str) -> None:
        self.controller.create_task(title, description, priority, deadline, status)
        self.refresh()

    def edit_task(self) -> None:
        task_id = self.selected_id()
        if task_id is None:
            return
        task = self.controller.database.get_task(task_id)
        if task:
            TaskForm(self.root, lambda *values: self._update_from_form(task_id, *values), task)

    def _update_from_form(self, task_id: int, title: str, description: str, priority: str,
                          deadline: str, status: str) -> None:
        self.controller.update_task(task_id, title, description, priority, deadline, status)
        self.refresh()

    def delete_task(self) -> None:
        task_id = self.selected_id()
        if task_id is not None and messagebox.askyesno("Delete task", "Delete the selected task?", parent=self.root):
            self.controller.delete_task(task_id)
            self.refresh()

    def undo(self) -> None:
        task = self.controller.undo()
        messagebox.showinfo("Undo", f"Restored: {task.title}" if task else "Nothing to undo.", parent=self.root)
        self.refresh()

    def process_next(self) -> None:
        task = self.controller.process_next_task()
        messagebox.showinfo("Task queue", f"Now processing: {task.title}" if task else "No pending tasks.", parent=self.root)
        self.refresh()

    def show_details(self) -> None:
        task_id = self.selected_id()
        if task_id is None:
            return
        task = self.controller.database.get_task(task_id)
        if task:
            messagebox.showinfo("Task details", f"Title: {task.title}\n\nDescription: {task.description or '—'}"
                                f"\n\nPriority: {task.priority_name}\nStatus: {task.status}"
                                f"\nDeadline: {task.deadline or '—'}\nCreated: {task.created_at}", parent=self.root)

    def view_logs(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Activity Log (Custom Linked List)")
        window.geometry("620x350")
        table = ttk.Treeview(window, columns=("time", "action", "task"), show="headings")
        for column, label, width in (("time", "Timestamp", 180), ("action", "Action", 210), ("task", "Task", 210)):
            table.heading(column, text=label)
            table.column(column, width=width)
        table.pack(fill="both", expand=True, padx=12, pady=12)
        for activity in self.controller.activities():
            table.insert("", "end", values=(activity.timestamp, activity.action, activity.task_name))

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        background, foreground = ("#202124", "#f1f3f4") if self.dark_mode else ("#f5f7fa", "#1f2937")
        self.root.configure(bg=background)
        self.style.configure("TFrame", background=background)
        self.style.configure("TLabel", background=background, foreground=foreground)
        self.style.configure("TLabelframe", background=background, foreground=foreground)
        self.style.configure("TLabelframe.Label", background=background, foreground=foreground)
        self.style.configure("Treeview", background="#303134" if self.dark_mode else "white", foreground=foreground,
                             fieldbackground="#303134" if self.dark_mode else "white")
