"""
Policy Manager / Camera Controller. This is the function the dashboard's
"Enable Camera" / "Disable Camera" buttons call directly, per the spec's
example: `enable_camera()`, `disable_camera()`.
"""
from typing import Tuple

from camera.registry_control import (
    enable_camera_registry,
    disable_camera_registry,
    get_registry_status,
)
from logger import log_activity, log_security_event


def enable_camera(username: str = "system") -> Tuple[bool, str]:
    success, message = enable_camera_registry()
    log_activity(username, "Camera Enabled" if success else f"Camera Enable FAILED ({message})")
    if not success:
        log_security_event(f"Camera enable failed for {username}: {message}")
    return success, message


def disable_camera(username: str = "system") -> Tuple[bool, str]:
    success, message = disable_camera_registry()
    log_activity(username, "Camera Disabled" if success else f"Camera Disable FAILED ({message})")
    if not success:
        log_security_event(f"Camera disable failed for {username}: {message}")
    return success, message


def get_camera_status() -> str:
    """Returns a human-friendly status: 'Enabled', 'Disabled', or 'Unknown'."""
    value = get_registry_status()
    if value == "Allow":
        return "Enabled"
    if value == "Deny":
        return "Disabled"
    return "Unknown"
