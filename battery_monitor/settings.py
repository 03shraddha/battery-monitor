"""
settings.py — Load, save, and validate app settings.

Settings are persisted to %APPDATA%\\BatteryMonitor\\settings.json.
Uses atomic write (write-then-rename) to prevent corruption on crash.
"""

import json
import os
from pathlib import Path

SETTINGS_DIR = Path(os.environ["APPDATA"]) / "BatteryMonitor"
SETTINGS_PATH = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS: dict = {
    "threshold": 20,        # alert when battery % falls to or below this
    "sound_enabled": True,  # play alarm beeps on alert
    "enabled": True,        # master on/off for monitoring
    "cooldown_seconds": 300 # minimum seconds between alerts
}


def load_settings() -> dict:
    """Return settings dict, creating the file with defaults if missing or corrupt."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return validate_settings(data)
        except (json.JSONDecodeError, OSError):
            pass  # fall through to defaults
    # Write defaults and return them
    settings = dict(DEFAULT_SETTINGS)
    save_settings(settings)
    return settings


def save_settings(settings: dict) -> None:
    """Atomically write settings to disk (write tmp then rename)."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = SETTINGS_PATH.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        os.replace(tmp_path, SETTINGS_PATH)  # atomic on Windows
    except OSError:
        pass  # settings save failure is non-fatal


def validate_settings(data: dict) -> dict:
    """Merge loaded data with defaults; clamp/coerce values to valid ranges."""
    # Merge: defaults provide any missing keys from future versions
    merged = {**DEFAULT_SETTINGS, **data}

    # Clamp threshold to 1-99
    try:
        merged["threshold"] = max(1, min(99, int(merged["threshold"])))
    except (ValueError, TypeError):
        merged["threshold"] = DEFAULT_SETTINGS["threshold"]

    # Coerce booleans
    for key in ("sound_enabled", "enabled"):
        if not isinstance(merged[key], bool):
            merged[key] = bool(merged[key])

    # Clamp cooldown to at least 60 seconds
    try:
        merged["cooldown_seconds"] = max(60, int(merged["cooldown_seconds"]))
    except (ValueError, TypeError):
        merged["cooldown_seconds"] = DEFAULT_SETTINGS["cooldown_seconds"]

    return merged
