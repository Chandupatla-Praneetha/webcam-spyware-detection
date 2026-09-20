"""
The login workflow the GUI calls, now a two-step process:

  1. authenticate_credentials() -- checks password (+ face for admins if
     requested). On success it does NOT finish the login yet: it emails a
     fresh OTP to the account's registered address and returns
     {"success": True, "user": ..., "otp_sent": bool, "otp_message": ...}.
     The GUI must then collect the OTP from the person and call step 2.

  2. verify_login_otp() -- checks the OTP the person typed. Only on a
     correct OTP is the login actually finalized (failed-attempt counter
     reset, "Login success" logged). A wrong/expired OTP is treated like
     any other failed login: counted, and triggers intrusion detection.

Any failure path (bad password, face mismatch, bad/expired OTP, unknown
username, locked account) triggers intruder capture + email alert.
"""
from typing import Dict, Any

from database.users import (
    get_user_by_username,
    increment_failed_attempts,
    reset_failed_attempts,
    is_locked,
)
from auth.password_auth import verify_password
from auth.face_auth import verify_face, is_face_recognition_available
from auth.otp import generate_and_send_otp, verify_otp
from alerts.intrusion_detector import handle_intrusion
from logger import log_activity


def authenticate_credentials(username: str, password: str, use_face: bool = False) -> Dict[str, Any]:
    """
    Step 1: password (+ optional face) check. On success, sends a login OTP
    and returns the user record so the GUI can prompt for that OTP next.
    Does NOT finalize the login (no failed-attempt reset, no "Login success"
    log entry yet -- that only happens once verify_login_otp() succeeds).
    """
    if is_locked(username):
        handle_intrusion("Login attempt on locked account", username)
        return {"success": False, "reason": "Account is locked due to too many failed attempts."}

    user = get_user_by_username(username)
    if user is None:
        handle_intrusion("Unknown username", username)
        return {"success": False, "reason": "Invalid username or password."}

    if not verify_password(password, user["password_hash"]):
        attempts = increment_failed_attempts(username)
        handle_intrusion("Wrong password", username)
        log_activity(username, "Failed login (bad password)")
        return {"success": False, "reason": f"Invalid username or password. ({attempts} failed attempt(s))"}

    # Password correct. Admins additionally require face verification IF they
    # have a face registered and the caller asked for it (checkbox in the GUI).
    if user["role"] == "admin" and use_face:
        if not is_face_recognition_available():
            return {"success": False, "reason": "Face recognition unavailable (opencv-contrib-python missing)."}
        if user["face_registered"]:
            matched, message = verify_face(username)
            if not matched:
                increment_failed_attempts(username)
                handle_intrusion("Face mismatch", username)
                log_activity(username, "Failed login (face mismatch)")
                return {"success": False, "reason": f"Face verification failed: {message}"}

    # Password (and face, if applicable) are correct -- now require an OTP
    # before the login is allowed to complete.
    otp_sent, otp_message = generate_and_send_otp(user["email"])
    log_activity(username, "Password verified, OTP sent" if otp_sent else f"Password verified, OTP send FAILED ({otp_message})")
    return {"success": True, "user": user, "otp_sent": otp_sent, "otp_message": otp_message}


def verify_login_otp(user: Dict[str, Any], entered_otp: str) -> Dict[str, Any]:
    """
    Step 2: checks the OTP the person entered after a successful password
    (+face) check. Only this call actually finalizes the login.
    """
    username = user["username"]
    if not verify_otp(user["email"], entered_otp):
        increment_failed_attempts(username)
        handle_intrusion("Invalid or expired OTP", username)
        log_activity(username, "Failed login (bad OTP)")
        return {"success": False, "reason": "Invalid or expired OTP."}

    reset_failed_attempts(username)
    log_activity(username, "Login success")
    return {"success": True, "user": user}


def logout(username: str) -> None:
    log_activity(username, "Logout")


def can_modify_camera(user: Dict[str, Any]) -> bool:
    """RBAC: only admins can enable/disable the camera or manage users/schedules."""
    return user.get("role") == "admin"
