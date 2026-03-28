"""
alert.py — Alert orchestration.

Coordinates the 4-step alert sequence:
  1. Dim screen (hardware or fallback overlay)
  2. Play alarm sound (in its own thread — winsound.Beep is blocking)
  3. Show "SYSTEM CRITICAL FAILURE" overlay for 5 seconds
  4. Restore screen brightness

Uses a finally: block to guarantee cleanup even if an exception occurs.
"""

import time
import threading
import winsound

from battery_monitor import brightness, overlay


def _play_alarm() -> None:
    """Three-beep alarm pattern using the Windows system beep (blocking)."""
    for _ in range(3):
        try:
            winsound.Beep(1000, 500)  # 1000 Hz for 500 ms
            winsound.Beep(800, 300)   # 800 Hz for 300 ms
            time.sleep(0.1)
        except Exception:
            break  # winsound can fail on some audio configurations


def _run_alert(state, settings: dict) -> None:
    """
    Full alert sequence. Runs on a dedicated daemon thread.
    Sets alert_active for its duration; clears it in finally:.
    """
    state.alert_active.set()
    state.last_alert_time = time.time()

    original_brightness = None
    try:
        # Step 1: Dim
        original_brightness = brightness.get_brightness()
        brightness.dim(original_brightness)

        # Step 2: Sound (non-blocking from this thread's perspective)
        if settings["sound_enabled"]:
            sound_thread = threading.Thread(
                target=_play_alarm, daemon=True, name="AlarmSound"
            )
            sound_thread.start()

        # Step 3: Overlay (blocks for `duration` seconds then returns)
        overlay.show_overlay(duration=5)

    finally:
        # Step 4: Always restore, always clear the event
        try:
            brightness.restore(original_brightness)
        except Exception:
            pass
        state.alert_active.clear()


def trigger_alert(state, settings: dict) -> None:
    """Non-blocking: launches the alert sequence on a daemon thread."""
    t = threading.Thread(
        target=_run_alert,
        args=(state, settings),
        daemon=True,
        name="AlertSequence"
    )
    t.start()
