"""
Login screen -- dark "cyber tool" themed, with the app logo and a centered
glass-panel card. Password + optional face verification for admins, and a
Forgot Password flow that emails an OTP.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from auth.login import authenticate_credentials, verify_login_otp
from auth.password_auth import hash_password
from auth.otp import generate_and_send_otp, verify_otp
from database.users import get_user_by_username, update_password
from auth.face_auth import is_face_recognition_available
from gui.theme import apply_theme, load_logo, COLORS, FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL


class LoginWindow(tk.Tk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Webcam Spyware Detection - Login")
        self.geometry("460x600")
        self.minsize(420, 560)
        apply_theme(self)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True)

        # ---- Brand header ----
        header = tk.Frame(outer, bg=COLORS["bg"])
        header.pack(pady=(36, 10))
        try:
            logo_img = load_logo(84)
            tk.Label(header, image=logo_img, bg=COLORS["bg"]).pack()
        except Exception:
            pass
        tk.Label(header, text="WEBCAM SPYWARE DETECTION", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(10, 0))
        tk.Label(header, text="Secure Access Control Console", font=FONT_SUBTITLE,
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack()

        # ---- Card ----
        card = tk.Frame(outer, bg=COLORS["panel"], highlightbackground=COLORS["border"],
                         highlightthickness=1, bd=0)
        card.pack(pady=26, padx=40, fill="x")

        pad = {"padx": 24}
        tk.Label(card, text="Username", font=FONT_NORMAL, bg=COLORS["panel"], fg=COLORS["text_dim"]).pack(
            anchor="w", **pad, pady=(22, 2))
        self.username_entry = ttk.Entry(card, style="TEntry", font=FONT_NORMAL)
        self.username_entry.pack(fill="x", **pad)

        tk.Label(card, text="Password", font=FONT_NORMAL, bg=COLORS["panel"], fg=COLORS["text_dim"]).pack(
            anchor="w", **pad, pady=(16, 2))
        self.password_entry = ttk.Entry(card, style="TEntry", font=FONT_NORMAL, show="*")
        self.password_entry.pack(fill="x", **pad)

        self.use_face_var = tk.BooleanVar(value=False)
        face_check = ttk.Checkbutton(
            card, text="Also verify face (admin accounts)", variable=self.use_face_var,
            style="TCheckbutton",
        )
        face_check.pack(anchor="w", **pad, pady=(14, 0))
        if not is_face_recognition_available():
            face_check.state(["disabled"])
            face_check.config(text="Face verification unavailable (check opencv-contrib-python install)")

        ttk.Button(card, text="LOG IN", style="Accent.TButton", command=self._attempt_login).pack(
            fill="x", **pad, pady=(20, 8))
        ttk.Button(card, text="Forgot Password?", style="Dark.TButton", command=self._forgot_password).pack(
            fill="x", **pad, pady=(0, 22))

        self.status_label = tk.Label(outer, text="", fg=COLORS["danger"], bg=COLORS["bg"],
                                      wraplength=380, justify="center", font=FONT_NORMAL)
        self.status_label.pack(pady=(0, 10))

        tk.Label(outer, text="Default admin: admin / ComplexPassword123!  (change after first login)",
                 font=("Segoe UI", 8), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="bottom", pady=14)

        self.bind("<Return>", lambda _e: self._attempt_login())
        self.username_entry.focus_set()

    def _attempt_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.config(text="Enter both username and password.")
            return

        result = authenticate_credentials(username, password, use_face=self.use_face_var.get())
        if not result["success"]:
            self.status_label.config(text=result["reason"])
            return

        user = result["user"]
        if not result.get("otp_sent"):
            self.status_label.config(
                text=f"Password correct, but the OTP email could not be sent: {result.get('otp_message')}"
            )
            return

        self.status_label.config(text="")
        otp = simpledialog.askstring(
            "OTP Verification",
            f"Password verified.\nA one-time code was emailed to {user['email']}.\nEnter it here:",
            parent=self,
        )
        if not otp:
            self.status_label.config(text="Login cancelled -- OTP was not entered.")
            return

        otp_result = verify_login_otp(user, otp)
        if not otp_result["success"]:
            self.status_label.config(text=otp_result["reason"])
            return

        self.destroy()
        self.on_success(otp_result["user"])

    def _forgot_password(self) -> None:
        username = simpledialog.askstring("Forgot Password", "Enter your username:", parent=self)
        if not username:
            return
        user = get_user_by_username(username)
        if not user:
            messagebox.showerror("Error", "No such user.")
            return

        sent, message = generate_and_send_otp(user["email"])
        if not sent:
            messagebox.showerror("Could not send OTP", message)
            return

        otp = simpledialog.askstring("OTP Verification", f"OTP sent to {user['email']}.\nEnter it here:", parent=self)
        if not otp:
            return
        if not verify_otp(user["email"], otp):
            messagebox.showerror("Error", "Invalid or expired OTP.")
            return

        new_password = simpledialog.askstring("Reset Password", "Enter your new password:", parent=self, show="*")
        if not new_password:
            return
        update_password(username, hash_password(new_password))
        messagebox.showinfo("Success", "Password reset. Please log in with your new password.")
