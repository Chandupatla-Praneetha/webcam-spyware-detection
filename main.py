"""
Entry point. Run with: python main.py

Startup sequence:
  1. Initialize the SQLite database (creates tables if missing).
  2. Create the default admin account on first run.
  3. Start the background scheduler thread.
  4. Show the login window; on success, show the dashboard; on logout,
     go back to the login window.
"""
import config
from database.database import init_db
from database.users import get_user_by_username, create_user
from auth.password_auth import hash_password
from scheduler import start_scheduler


def _ensure_default_admin() -> None:
    if get_user_by_username(config.DEFAULT_ADMIN_USERNAME) is None:
        create_user(
            username=config.DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(config.DEFAULT_ADMIN_PASSWORD),
            email=config.ADMIN_EMAIL,
            role="admin",
        )
        print(f"Created default admin account: {config.DEFAULT_ADMIN_USERNAME} / {config.DEFAULT_ADMIN_PASSWORD}")
        print("IMPORTANT: change this password after first login, and set a real ADMIN_EMAIL in config.py.")


def _show_login() -> None:
    from gui.login_window import LoginWindow

    def on_success(user: dict) -> None:
        _show_dashboard(user)

    LoginWindow(on_success).mainloop()


def _show_dashboard(user: dict) -> None:
    from gui.dashboard import Dashboard

    def on_logout() -> None:
        _show_login()

    Dashboard(user, on_logout).mainloop()


def main() -> None:
    init_db()
    _ensure_default_admin()
    start_scheduler()
    _show_login()


if __name__ == "__main__":
    main()
