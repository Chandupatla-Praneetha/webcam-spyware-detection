"""
Admin-only: create/delete camera on/off schedules as a TIME RANGE, e.g.
"5:00 PM to 6:00 PM" -- the camera is enabled at the from-time and
disabled at the to-time. Actual execution happens in scheduler.py
(background thread started in main.py).
"""
import re
import tkinter as tk
from tkinter import ttk, messagebox

from database.schedules import add_schedule, list_schedules, delete_schedule
from logger import log_activity
from gui.theme import apply_theme, COLORS, FONT_NORMAL

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _to_12h(time_24h: str) -> str:
    """'17:00' -> '5:00 PM' for a friendlier display in the table."""
    try:
        hour, minute = time_24h.split(":")
        hour = int(hour)
        suffix = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12 or 12
        return f"{hour_12}:{minute} {suffix}"
    except Exception:
        return time_24h


class ScheduleWindow(tk.Toplevel):
    def __init__(self, parent, current_user: dict, on_change=None):
        super().__init__(parent)
        if not current_user or current_user.get("role") != "admin":
            messagebox.showerror("Access Denied", "Only an authenticated administrator can manage schedules.")
            self.destroy()
            return

        self.current_user = current_user
        self.on_change = on_change
        self.title("Manage Schedules")
        self.geometry("520x460")
        apply_theme(self)
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        tk.Label(self, text="CAMERA SCHEDULES", bg=COLORS["bg"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))

        table_frame = tk.Frame(self, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        columns = ("id", "from", "to", "created_by")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=9)
        for col, w in (("id", 40), ("from", 110), ("to", 110), ("created_by", 120)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(self, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        form.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(form, text="ADD SCHEDULE  --  camera stays ON during this window (24h time, e.g. 17:00)",
                 bg=COLORS["panel"], fg=COLORS["text_dim"], font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(10, 8))

        tk.Label(form, text="From time", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=0, padx=6)
        tk.Label(form, text="To time", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=1, padx=6)

        self.from_entry = ttk.Entry(form, width=10, style="TEntry")
        self.from_entry.insert(0, "17:00")
        self.to_entry = ttk.Entry(form, width=10, style="TEntry")
        self.to_entry.insert(0, "18:00")

        self.from_entry.grid(row=2, column=0, padx=6, pady=(0, 12))
        self.to_entry.grid(row=2, column=1, padx=6, pady=(0, 12))
        ttk.Button(form, text="Add Schedule", style="Accent.TButton", command=self._add).grid(
            row=2, column=2, padx=10, pady=(0, 12))

        ttk.Button(self, text="Delete Selected", style="Danger.TButton", command=self._delete_selected).pack(
            anchor="w", padx=16, pady=(0, 16))

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for row in list_schedules():
            self.tree.insert("", "end", iid=str(row["id"]), values=(
                row["id"], _to_12h(row["start_time"]), _to_12h(row["end_time"]), row["created_by"],
            ))

    def _add(self) -> None:
        start_time = self.from_entry.get().strip()
        end_time = self.to_entry.get().strip()
        if not _TIME_PATTERN.match(start_time) or not _TIME_PATTERN.match(end_time):
            messagebox.showerror("Error", "Both times must be in HH:MM 24-hour format, e.g. 17:00")
            return
        if start_time == end_time:
            messagebox.showerror("Error", "From time and To time cannot be the same.")
            return

        add_schedule(start_time, end_time, self.current_user["username"])
        log_activity(
            self.current_user["username"],
            f"Schedule Added (camera ON {_to_12h(start_time)} to {_to_12h(end_time)})",
        )
        self._refresh()
        if self.on_change:
            self.on_change()

    def _delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        delete_schedule(int(selection[0]))
        log_activity(self.current_user["username"], "Schedule Deleted")
        self._refresh()
        if self.on_change:
            self.on_change()
