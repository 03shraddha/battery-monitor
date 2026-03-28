"""
brightness.py — Screen dimming with hardware primary and tkinter fallback.

Primary: screen_brightness_control (SBC) — works on most laptop displays.
Fallback: semi-transparent black tkinter window — works on all hardware.

The fallback window reference is stored here so restore() can destroy it.
"""

import threading
import tkinter as tk

# Module-level reference to the fallback dim window (if active)
_dim_window: tk.Tk | None = None
_dim_lock = threading.Lock()


def get_brightness() -> int | None:
    """Return current brightness (0-100) or None if hardware control unavailable."""
    try:
        import screen_brightness_control as sbc
        result = sbc.get_brightness()
        if result:
            return int(result[0])
    except Exception:
        pass
    return None


def dim(original: int | None) -> None:
    """Dim the screen. Uses SBC if available, otherwise dark overlay."""
    if original is not None:
        try:
            import screen_brightness_control as sbc
            target = max(0, original - 70)
            sbc.set_brightness(target)
            return  # primary path succeeded
        except Exception:
            pass  # fall through to overlay

    # Fallback: near-opaque black tkinter overlay window
    _show_dim_overlay()


def restore(original: int | None) -> None:
    """Restore the screen to its original brightness."""
    if original is not None:
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(original)
            return  # primary path succeeded
        except Exception:
            pass  # fall through to overlay removal

    _hide_dim_overlay()


# ---------------------------------------------------------------------------
# Fallback overlay helpers (run on calling thread — must be in alert thread)
# ---------------------------------------------------------------------------

def _show_dim_overlay() -> None:
    """Create a near-opaque fullscreen black window to simulate dimming."""
    global _dim_window
    with _dim_lock:
        if _dim_window is not None:
            return  # already showing

        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.80)   # 80% opaque = very dark
        root.configure(bg="black")
        root.overrideredirect(True)       # no title bar
        root.update()                     # force immediate render
        _dim_window = root


def _hide_dim_overlay() -> None:
    """Destroy the fallback dim overlay window if it exists."""
    global _dim_window
    with _dim_lock:
        if _dim_window is not None:
            try:
                _dim_window.destroy()
            except Exception:
                pass
            _dim_window = None
