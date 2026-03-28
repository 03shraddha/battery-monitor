"""
monitor.py — Battery polling daemon thread.

Polls psutil every 30 seconds. Fires alert_callback when all conditions are met:
  - monitoring is enabled
  - battery is NOT plugged in (ignore when charging)
  - battery % is at or below the configured threshold
  - no alert is currently running (alert_active event is not set)
  - cooldown period has elapsed since the last alert
"""

import time
import threading
import psutil


def monitor_loop(state, settings: dict, alert_callback) -> None:
    """Main polling loop — runs on a daemon thread."""
    while True:
        battery = psutil.sensors_battery()

        if battery is not None:
            with state.lock:
                state.battery_percent = int(battery.percent)
                state.is_plugged_in = battery.power_plugged

            cooldown_elapsed = (
                time.time() - state.last_alert_time
            ) > settings["cooldown_seconds"]

            should_alert = (
                state.enabled
                and not state.is_plugged_in          # ignore when charging
                and state.battery_percent <= settings["threshold"]
                and not state.alert_active.is_set()  # don't overlap alerts
                and cooldown_elapsed
            )

            if should_alert:
                alert_callback()

        time.sleep(30)


def start_monitor(state, settings: dict, alert_callback) -> threading.Thread:
    """Start the monitor loop on a daemon thread and return it."""
    t = threading.Thread(
        target=monitor_loop,
        args=(state, settings, alert_callback),
        daemon=True,  # dies automatically when main thread exits
        name="BatteryMonitor"
    )
    t.start()
    return t
