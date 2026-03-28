"""
main.py — Entry point and shared application state.

Threading model:
  - Main thread: pystray Win32 message loop (required by pystray on Windows)
  - Daemon thread: battery monitor polling loop
  - Per-alert daemon thread: alert sequence (dim, sound, overlay, restore)
  - Per-alert sound daemon thread: winsound.Beep (blocking, isolated)

AppState holds all shared mutable state with threading primitives for safety.
"""

import sys
import os
import threading
import time
from dataclasses import dataclass, field

# Ensure the project root is on sys.path so this file can be run directly
# with `python battery_monitor/main.py` as well as `python -m battery_monitor.main`
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from battery_monitor.settings import load_settings
from battery_monitor.monitor import start_monitor
from battery_monitor.alert import trigger_alert
from battery_monitor.tray import build_tray
from battery_monitor.startup import apply_startup_registry


@dataclass
class AppState:
    """Thread-safe shared state for the app."""
    # Mutable battery state (protected by lock)
    battery_percent: int = 100
    is_plugged_in: bool = True

    # Threading primitives
    lock: threading.Lock = field(default_factory=threading.Lock)
    alert_active: threading.Event = field(default_factory=threading.Event)

    # Alert timing (read/written only from monitor thread or main thread)
    last_alert_time: float = field(default_factory=lambda: 0.0)

    # Master enable flag (also stored in settings; mirrored here for fast access)
    enabled: bool = True


def main() -> None:
    # Load persisted settings (creates defaults on first run)
    settings = load_settings()

    # Build shared state, seeding enabled from settings
    state = AppState(enabled=settings["enabled"])

    # Register for Windows startup (idempotent — safe to call every launch)
    apply_startup_registry()

    # Build alert callback (captures state + settings)
    def on_alert():
        trigger_alert(state, settings)

    # Start battery monitor on a daemon thread
    start_monitor(state, settings, on_alert)

    # Build tray icon (does not block yet)
    icon = build_tray(state, settings)

    # Run tray on main thread — blocks until user clicks Quit
    icon.run()


if __name__ == "__main__":
    main()
