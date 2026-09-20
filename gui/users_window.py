"""
Admin-only: add/delete users, register a user's face, unlock accounts.

RBAC is enforced twice: (1) structurally -- this window is only ever
opened from Dashboard's admin-only control panel, which itself only
renders after a successful login (password + OTP) via auth.login; (2) defensively --
the constructor re-checks current_user["role"] == "admin" itself and
refuses to open otherwise, in case this class is ever invoked some other
way in the future.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from database.users import list_users, create_user, delete_user, set_face_registered, unlock_user
from auth.password_auth import hash_password
from auth.face_auth import register_admin_face, is_face_recognition_available
from logger import log_activity
from gui.theme import apply_theme, COLORS, FONT_NORMAL


class UsersWindow(tk.Toplevel):
    def __init__(self, parent, current_user: dict, on_change=None):
        super().__init__(parent)
        if not current_user or current_user.get("role") != "admin":
            messagebox.showerror("Access Denied", "Only an authenticated administrator can manage users.")
            self.destroy()
            return

        self.current_user = current_user
        self.on_change = on_change
        self.title("Manage Users")
        self.geometry("680x460")
        apply_theme(self)
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        tk.Label(self, text="USER MANAGEMENT", bg=COLORS["bg"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))

        table_frame = tk.Frame(self, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        columns = ("username", "email", "role", "face", "failed", "locked")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=9)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=95)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(self, bg=COLORS["panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        form.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(form, text="ADD USER (admin only)", bg=COLORS["panel"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(10, 6))

        tk.Label(form, text="Username", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=0, padx=6)
        tk.Label(form, text="Email", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=1, padx=6)
        tk.Label(form, text="Password", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=2, padx=6)
        tk.Label(form, text="Role", bg=COLORS["panel"], fg=COLORS["text_dim"], font=FONT_NORMAL).grid(row=1, column=3, padx=6)

        self.username_entry = ttk.Entry(form, width=14, style="TEntry")
        self.email_entry = ttk.Entry(form, width=18, style="TEntry")
        self.password_entry = ttk.Entry(form, width=14, style="TEntry", show="*")
        self.role_var = tk.StringVar(value="user")

        self.username_entry.grid(row=2, column=0, padx=6, pady=(0, 12))
        self.email_entry.grid(row=2, column=1, padx=6, pady=(0, 12))
        self.password_entry.grid(row=2, column=2, padx=6, pady=(0, 12))
        ttk.Combobox(form, textvariable=self.role_var, values=["user", "admin"], width=8,
                     state="readonly", style="TCombobox").grid(row=2, column=3, padx=6, pady=(0, 12))
        ttk.Button(form, text="Add User", style="Accent.TButton", command=self._add_user).grid(row=2, column=4, padx=10, pady=(0, 12))

        actions = tk.Frame(self, bg=COLORS["bg"])
        actions.pack(fill="x", padx=16, pady=(0, 16))
        ttk.Button(actions, text="Delete Selected", style="Danger.TButton", command=self._delete_selected).pack(side="left")
        ttk.Button(actions, text="Unlock Selected", style="Dark.TButton", command=self._unlock_selected).pack(side="left", padx=6)
        register_btn = ttk.Button(actions, text="Register Face for Selected (admin)", style="Dark.TButton", command=self._register_face)
        register_btn.pack(side="left", padx=6)
        if not is_face_recognition_available():
            register_btn.state(["disabled"])

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for u in list_users():
            self.tree.insert("", "end", iid=u["username"], values=(
                u["username"], u["email"], u["role"],
                "Yes" if u["face_registered"] else "No",
                u["failed_attempts"], "Yes" if u["locked"] else "No",
            ))

    def _selected_username(self):
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _add_user(self) -> None:
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()
        if not (username and email and password):
            messagebox.showerror("Error", "All fields are required.")
            return
        ok = create_user(username, hash_password(password), email, role)
        if not ok:
            messagebox.showerror("Error", "Username already exists.")
            return
        log_activity(self.current_user["username"], f"Added user '{username}' (role={role})")
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self._refresh()
        if self.on_change:
            self.on_change()

    def _delete_selected(self) -> None:
        username = self._selected_username()
        if not username:
            return
        if username == "admin":
            messagebox.showerror("Error", "Cannot delete the default admin account.")
            return
        if messagebox.askyesno("Confirm", f"Delete user '{username}'?"):
            delete_user(username)
            log_activity(self.current_user["username"], f"Deleted user '{username}'")
            self._refresh()
            if self.on_change:
                self.on_change()

    def _unlock_selected(self) -> None:
        username = self._selected_username()
        if not username:
            return
        unlock_user(username)
        log_activity(self.current_user["username"], f"Unlocked user '{username}'")
        self._refresh()

    def _register_face(self) -> None:
        username = self._selected_username()
        if not username:
            messagebox.showinfo("Select a user", "Select a user row first.")
            return
        messagebox.showinfo("Face Registration", "Look at the webcam. Capturing samples now...")
        success, message = register_admin_face(username)
        if success:
            set_face_registered(username, True)
            log_activity(self.current_user["username"], f"Registered face for '{username}'")
        (messagebox.showinfo if success else messagebox.showerror)("Face Registration", message)
        self._refresh()
