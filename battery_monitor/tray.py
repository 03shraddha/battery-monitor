"""
tray.py — System tray icon and menu.

Builds a pystray Icon with a Pillow-generated battery icon.
Menu items use lambda text to reflect current settings dynamically.
Settings changes are saved immediately and the icon tooltip is updated.
"""

import threading
import tkinter as tk
import tkinter.simpledialog as simpledialog
import pystray
from PIL import Image, ImageDraw


# ---------------------------------------------------------------------------
# Icon generation (pure Pillow — no external image files needed)
# ---------------------------------------------------------------------------

def _create_icon_image(threshold: int) -> Image.Image:
    """Generate a simple battery icon (64x64) with the threshold % printed."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Battery body
    body = [8, 16, 52, 52]
    draw.rectangle(body, outline="white", width=3)

    # Battery cap (positive terminal)
    draw.rectangle([22, 10, 42, 16], fill="white")

    # Fill level (green)
    fill_height = int(32 * (threshold / 100))
    fill_y1 = 52 - fill_height
    draw.rectangle([11, fill_y1, 49, 49], fill="#00cc44")

    # Threshold text inside battery
    draw.text((18, 28), f"{threshold}%", fill="white")

    return img


# ---------------------------------------------------------------------------
# Settings dialog (runs in its own thread to not block pystray)
# ---------------------------------------------------------------------------

def _open_threshold_dialog(state, settings: dict, icon: pystray.Icon) -> None:
    """Open a tkinter dialog to let the user change the threshold."""
    def _dialog():
        root = tk.Tk()
        root.withdraw()  # hide the blank root window
        new_val = simpledialog.askinteger(
            "Set Threshold",
            "Alert when battery falls to or below (1-99)%:",
            initialvalue=settings["threshold"],
            minvalue=1,
            maxvalue=99,
            parent=root,
        )
        root.destroy()
        if new_val is not None:
            settings["threshold"] = new_val
            from battery_monitor.settings import save_settings
            save_settings(settings)
            # Regenerate icon with updated threshold number
            icon.icon = _create_icon_image(new_val)
            icon.title = f"Battery Monitor — Alert at {new_val}%"

    t = threading.Thread(target=_dialog, daemon=True, name="SettingsDialog")
    t.start()


# ---------------------------------------------------------------------------
# Menu callbacks
# ---------------------------------------------------------------------------

def _toggle_sound(settings: dict) -> None:
    settings["sound_enabled"] = not settings["sound_enabled"]
    from battery_monitor.settings import save_settings
    save_settings(settings)


def _toggle_enabled(state, settings: dict, icon: pystray.Icon) -> None:
    settings["enabled"] = not settings["enabled"]
    state.enabled = settings["enabled"]
    from battery_monitor.settings import save_settings
    save_settings(settings)
    # Update tooltip
    status = "enabled" if settings["enabled"] else "disabled"
    icon.title = f"Battery Monitor — {status}"


def _quit_app(icon: pystray.Icon) -> None:
    icon.stop()  # stops pystray loop → main() returns → process exits


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def build_tray(state, settings: dict) -> pystray.Icon:
    """
    Build and return the pystray Icon. Call icon.run() on the main thread
    to start the Win32 message loop (it blocks until _quit_app is called).
    """
    icon_image = _create_icon_image(settings["threshold"])

    # Placeholder; icon is injected into lambdas after creation
    icon_ref: list[pystray.Icon] = []  # list used as mutable cell

    def menu_threshold_text(item):
        return f"Set threshold (now {settings['threshold']}%)"

    def menu_sound_text(item):
        state_str = "On" if settings["sound_enabled"] else "Off"
        return f"Sound: {state_str}"

    def menu_enabled_text(item):
        return "Enabled" if settings["enabled"] else "Disabled"

    menu = pystray.Menu(
        pystray.MenuItem("Battery Monitor", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            menu_threshold_text,
            lambda item: _open_threshold_dialog(state, settings, icon_ref[0]),
        ),
        pystray.MenuItem(
            menu_sound_text,
            lambda item: _toggle_sound(settings),
        ),
        pystray.MenuItem(
            menu_enabled_text,
            lambda item: _toggle_enabled(state, settings, icon_ref[0]),
            checked=lambda item: settings["enabled"],
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "Quit",
            lambda item: _quit_app(icon_ref[0]),
        ),
    )

    icon = pystray.Icon(
        "BatteryMonitor",
        icon_image,
        f"Battery Monitor — Alert at {settings['threshold']}%",
        menu,
    )
    icon_ref.append(icon)  # inject into closure cells
    return icon
