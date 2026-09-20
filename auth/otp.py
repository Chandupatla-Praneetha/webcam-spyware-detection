"""
One-Time-Password flow used for "Forgot Password via SMTP Email".
Keeps pending OTPs in memory (fine for a single-instance desktop app).
"""
import random
import time
from typing import Tuple

import config
from alerts.email_alert import send_email

# email -> (otp_code, expires_at_epoch_seconds)
_pending_otps = {}


def generate_and_send_otp(email: str) -> Tuple[bool, str]:
    """Generate a 6-digit OTP, email it, and remember it for verification."""
    otp_code = f"{random.randint(0, 999999):06d}"
    expires_at = time.time() + config.OTP_VALIDITY_SECONDS
    _pending_otps[email] = (otp_code, expires_at)

    subject = "Your Password Reset OTP"
    body = (
        f"Your one-time password (OTP) is: {otp_code}\n\n"
        f"This code expires in {config.OTP_VALIDITY_SECONDS // 60} minutes.\n"
        f"If you did not request a password reset, please ignore this email."
    )
    sent, error = send_email(subject, body, email)
    if not sent:
        return False, error
    return True, "OTP sent."


def verify_otp(email: str, entered_otp: str) -> bool:
    record = _pending_otps.get(email)
    if not record:
        return False
    otp_code, expires_at = record
    if time.time() > expires_at:
        _pending_otps.pop(email, None)
        return False
    if entered_otp.strip() == otp_code:
        _pending_otps.pop(email, None)  # one-time use
        return True
    return False
