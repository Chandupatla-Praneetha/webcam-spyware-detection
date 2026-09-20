"""
Security Dashboard -- dark "SOC console" themed. Shows camera status,
counts, recent activity. Admins get camera controls + user/schedule
management; regular users get a read-only view, per RBAC.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from auth.login import can_modify_camera, logout
from camera.camera_control import enable_camera, disable_camera, get_camera_status
from database.logs import get_recent_activity, get_intruder_logs, get_failed_login_count, get_intruder_alert_count
from database.users import list_users
from reports import generate_security_report
from gui.theme import apply_theme, load_logo, COLORS, FONT_TITLE, FONT_HEADING, FONT_NORMAL


class Dashboard(tk.Tk):
    def __init__(self, user: dict, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.title(f"Webcam Spyware Detection - {user['username']} ({user['role']})")
        self.geometry("980x640")
        self.minsize(860, 560)
        apply_theme(self)
        self._build_ui()
        self._refresh()

    # ---------- layout ----------
    def _build_ui(self) -> None:
        self._build_topbar()

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=(14, 20))

        self._build_stat_row(body)

        if can_modify_camera(self.user):
            self._build_admin_controls(body)
        else:
            tk.Label(body, text="View-only account -- camera control is restricted to administrators.",
                     bg=COLORS["bg"], fg=COLORS["text_dim"], font=FONT_NORMAL).pack(anchor="w", pady=(4, 10))

        self._build_logs(body)

    def _build_topbar(self) -> None:
        bar = tk.Frame(self, bg=COLORS["panel"], height=64)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        left = tk.Frame(bar, bg=COLORS["panel"])
        left.pack(side="left", padx=18, pady=10)
        try:
            logo_img = load_logo(38)
            tk.Label(left, image=logo_img, bg=COLORS["panel"]).pack(side="left", padx=(0, 10))
        except Exception:
            pass
        text_col = tk.Frame(left, bg=COLORS["panel"])
        text_col.pack(side="left")
        tk.Label(text_col, text="WEBCAM SPYWARE DETECTION", bg=COLORS["panel"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(text_col, text=f"Signed in as {self.user['username']}  ·  role: {self.user['role']}",
                 bg=COLORS["panel"], fg=COLORS["text_dim"], font=("Segoe UI", 9)).pack(anchor="w")

        right = tk.Frame(bar, bg=COLORS["panel"])
        right.pack(side="right", padx=16)
        ttk.Button(right, text="Logout", style="Dark.TButton", command=self._logout).pack(side="right", padx=4, pady=14)
        ttk.Button(right, text="Refresh", style="Dark.TButton", command=self._refresh).pack(side="right", padx=4, pady=14)

        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill="x", side="top")

    def _build_stat_row(self, parent) -> None:
        row = tk.Frame(parent, bg=COLORS["bg"])
        row.pack(fill="x", pady=(0, 16))
        self.status_vars = {
            "camera": tk.StringVar(value="..."),
            "users": tk.StringVar(value="..."),
            "failed": tk.StringVar(value="..."),
            "intruders": tk.StringVar(value="..."),
        }
        self._stat_card(row, "CAMERA STATUS", self.status_vars["camera"])
        self._stat_card(row, "USERS COUNT", self.status_vars["users"])
        self._stat_card(row, "FAILED LOGINS", self.status_vars["failed"])
        self._stat_card(row, "INTRUDER ALERTS", self.status_vars["intruders"])

    def _stat_card(self, parent, title: str, var: tk.StringVar) -> None:
        card = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(side="left", expand=True, fill="both", padx=6)
        tk.Frame(card, bg=COLORS["accent"], height=3).pack(fill="x", side="top")
        tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text_dim"], font=("Segoe UI", 9, "bold")).pack(
            pady=(14, 2))
        tk.Label(card, textvariable=var, bg=COLORS["panel"], fg=COLORS["accent"], font=("Segoe UI", 20, "bold")).pack(
            pady=(0, 16))

    def _build_admin_controls(self, parent) -> None:
        panel = tk.Frame(parent, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        panel.pack(fill="x", pady=(0, 16))
        tk.Label(panel, text="ADMIN CONTROLS", bg=COLORS["panel"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        btns = tk.Frame(panel, bg=COLORS["panel"])
        btns.pack(fill="x", padx=12, pady=(0, 14))
        ttk.Button(btns, text="Enable Camera", style="Accent.TButton", command=self._enable_camera).pack(side="left", padx=6)
        ttk.Button(btns, text="Disable Camera", style="Dark.TButton", command=self._disable_camera).pack(side="left", padx=6)
        ttk.Button(btns, text="Manage Users", style="Dark.TButton", command=self._open_users_window).pack(side="left", padx=6)
        ttk.Button(btns, text="Manage Schedules", style="Dark.TButton", command=self._open_schedule_window).pack(side="left", padx=6)
        ttk.Button(btns, text="Generate PDF Report", style="Dark.TButton", command=self._generate_report).pack(side="left", padx=6)

    def _build_logs(self, parent) -> None:
        logs = tk.Frame(parent, bg=COLORS["bg"])
        logs.pack(fill="both", expand=True)

        left = tk.Frame(logs, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="RECENT ACTIVITY", bg=COLORS["panel"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        self.activity_tree = ttk.Treeview(left, columns=("time", "user", "action"), show="headings", height=10)
        for col, w in (("time", 150), ("user", 100), ("action", 260)):
            self.activity_tree.heading(col, text=col.capitalize())
            self.activity_tree.column(col, width=w)
        self.activity_tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        right = tk.Frame(logs, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="INTRUDER ALERTS", bg=COLORS["panel"], fg=COLORS["danger"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        self.intruder_tree = ttk.Treeview(right, columns=("time", "reason", "user"), show="headings", height=10)
        for col, w in (("time", 150), ("reason", 160), ("user", 110)):
            self.intruder_tree.heading(col, text=col.capitalize())
            self.intruder_tree.column(col, width=w)
        self.intruder_tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # ---------- data ----------
    def _refresh(self) -> None:
        self.status_vars["camera"].set(get_camera_status())
        self.status_vars["users"].set(str(len(list_users())))
        self.status_vars["failed"].set(str(get_failed_login_count()))
        self.status_vars["intruders"].set(str(get_intruder_alert_count()))

        self.activity_tree.delete(*self.activity_tree.get_children())
        for row in get_recent_activity(40):
            self.activity_tree.insert("", "end", values=(row["timestamp"], row["username"], row["action"]))

        self.intruder_tree.delete(*self.intruder_tree.get_children())
        for row in get_intruder_logs(40):
            self.intruder_tree.insert("", "end", values=(row["timestamp"], row["reason"], row["username"]))

    # ---------- actions ----------
    def _enable_camera(self) -> None:
        success, message = enable_camera(self.user["username"])
        (messagebox.showinfo if success else messagebox.showerror)("Enable Camera", message)
        self._refresh()

    def _disable_camera(self) -> None:
        success, message = disable_camera(self.user["username"])
        (messagebox.showinfo if success else messagebox.showerror)("Disable Camera", message)
        self._refresh()

    def _generate_report(self) -> None:
        path = generate_security_report()
        messagebox.showinfo("Report Generated", f"Saved to:\n{path}")

    def _open_users_window(self) -> None:
        from gui.users_window import UsersWindow
        UsersWindow(self, current_user=self.user, on_change=self._refresh)

    def _open_schedule_window(self) -> None:
        from gui.schedule_window import ScheduleWindow
        ScheduleWindow(self, current_user=self.user, on_change=self._refresh)

    def _logout(self) -> None:
        logout(self.user["username"])
        self.destroy()
        self.on_logout()
