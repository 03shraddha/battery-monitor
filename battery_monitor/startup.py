"""
startup.py — Windows startup registry management.

Adds the app to HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run so it
launches automatically on login. Uses HKCU (not HKLM) — no admin rights needed.

apply_startup_registry() is idempotent: safe to call on every launch.
"""

import sys
import winreg

_STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "BatteryMonitor"


def apply_startup_registry() -> None:
    """Register the app for startup. Silently ignores permission errors."""
    exe_path = sys.executable  # resolves to the .exe path when packaged
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _STARTUP_KEY,
            access=winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
    except (PermissionError, OSError):
        pass  # non-fatal: startup is a nice-to-have


def remove_startup_registry() -> None:
    """Remove the startup registry entry (e.g., on uninstall)."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _STARTUP_KEY,
            access=winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, _APP_NAME)
    except (FileNotFoundError, PermissionError, OSError):
        pass
