"""
Registry Manager. Flips the Windows privacy setting that controls whether
apps can access the webcam, mirroring what Settings > Privacy > Camera does.

IMPORTANT (read before running on Windows):
- HKEY_CURRENT_USER (the default here) does NOT require admin rights and is
  exactly what Windows itself writes when you toggle camera privacy in Settings.
- HKEY_LOCAL_MACHINE (config.USE_HKLM = True) is the system-wide policy and
  DOES require running Python "as Administrator", or every write below will
  raise PermissionError.
- This module is Windows-only (it needs `winreg`, part of the Python stdlib
  on Windows only). On macOS/Linux the import fails gracefully and every
  function returns False with a clear reason, so the rest of the app (GUI,
  DB, alerts) can still be developed/tested cross-platform.
"""
from typing import Tuple

import config

try:
    import winreg
    _WINREG_AVAILABLE = True
except ImportError:
    _WINREG_AVAILABLE = False


def _get_root_and_hive():
    if config.USE_HKLM:
        return winreg.HKEY_LOCAL_MACHINE, "HKLM"
    return winreg.HKEY_CURRENT_USER, "HKCU"


def _set_webcam_value(value: str) -> Tuple[bool, str]:
    if not _WINREG_AVAILABLE:
        return False, "winreg is only available on Windows. Registry control skipped."

    root, hive_name = _get_root_and_hive()
    try:
        key = winreg.CreateKeyEx(root, config.REGISTRY_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True, f"Registry updated under {hive_name}\\{config.REGISTRY_PATH}"
    except PermissionError:
        return False, "Permission denied. Try running the app as Administrator (needed for HKLM)."
    except OSError as exc:
        return False, f"Registry write failed: {exc}"


def enable_camera_registry() -> Tuple[bool, str]:
    return _set_webcam_value("Allow")


def disable_camera_registry() -> Tuple[bool, str]:
    return _set_webcam_value("Deny")


def get_registry_status() -> str:
    """Returns 'Allow', 'Deny', or 'Unknown' (e.g. key never set, or non-Windows)."""
    if not _WINREG_AVAILABLE:
        return "Unknown (non-Windows)"
    root, _ = _get_root_and_hive()
    try:
        key = winreg.OpenKey(root, config.REGISTRY_PATH, 0, winreg.KEY_READ)
        value, _type = winreg.QueryValueEx(key, "Value")
        winreg.CloseKey(key)
        return value
    except OSError:
        return "Unknown"
