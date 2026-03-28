"""
overlay.py — Fullscreen "SYSTEM CRITICAL FAILURE" alert overlay.

Creates a fresh Tk() instance per alert call (tkinter is not thread-safe;
running a new mainloop per invocation in its own thread is the safe pattern).

The overlay auto-dismisses after `duration` seconds via root.after().
A countdown label counts down so the user knows it will go away on its own.
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import math


def _draw_angry_cat(size: int = 300) -> Image.Image:
    """Generate an angry cat face using Pillow. Returns an RGBA image."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2 + 20
    r = int(size * 0.38)

    # --- Head ---
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#cc6600", outline="#ff8800", width=4)

    # --- Ears (pointy triangles) ---
    ear_h = int(r * 0.75)
    ear_w = int(r * 0.42)
    # Left ear
    d.polygon([
        (cx - r + 10, cy - r + 20),
        (cx - r - ear_w + 20, cy - r - ear_h),
        (cx - r // 2, cy - r + 5),
    ], fill="#cc6600", outline="#ff8800", width=3)
    # Inner left ear
    d.polygon([
        (cx - r + 18, cy - r + 15),
        (cx - r - ear_w + 30, cy - r - ear_h + 18),
        (cx - r // 2 + 5, cy - r + 10),
    ], fill="#ff9999")
    # Right ear
    d.polygon([
        (cx + r - 10, cy - r + 20),
        (cx + r + ear_w - 20, cy - r - ear_h),
        (cx + r // 2, cy - r + 5),
    ], fill="#cc6600", outline="#ff8800", width=3)
    # Inner right ear
    d.polygon([
        (cx + r - 18, cy - r + 15),
        (cx + r + ear_w - 30, cy - r - ear_h + 18),
        (cx + r // 2 - 5, cy - r + 10),
    ], fill="#ff9999")

    # --- Eyes (angry narrow slits) ---
    eye_y = cy - int(r * 0.15)
    eye_ox = int(r * 0.38)
    eye_w, eye_h = int(r * 0.30), int(r * 0.18)
    # Left eye (angry: top-left corner raised)
    d.ellipse([cx - eye_ox - eye_w, eye_y - eye_h, cx - eye_ox + eye_w, eye_y + eye_h],
              fill="yellow", outline="#333300", width=2)
    d.ellipse([cx - eye_ox - eye_w // 3, eye_y - eye_h // 2,
               cx - eye_ox + eye_w // 3, eye_y + eye_h // 2],
              fill="black")
    # Left angry brow (slants down toward nose)
    d.line([(cx - eye_ox - eye_w - 5, eye_y - eye_h - 18),
            (cx - eye_ox + eye_w + 5, eye_y - eye_h - 4)],
           fill="#330000", width=8)
    # Right eye
    d.ellipse([cx + eye_ox - eye_w, eye_y - eye_h, cx + eye_ox + eye_w, eye_y + eye_h],
              fill="yellow", outline="#333300", width=2)
    d.ellipse([cx + eye_ox - eye_w // 3, eye_y - eye_h // 2,
               cx + eye_ox + eye_w // 3, eye_y + eye_h // 2],
              fill="black")
    # Right angry brow (slants down toward nose)
    d.line([(cx + eye_ox - eye_w - 5, eye_y - eye_h - 4),
            (cx + eye_ox + eye_w + 5, eye_y - eye_h - 18)],
           fill="#330000", width=8)

    # --- Nose ---
    nose_y = cy + int(r * 0.18)
    nose_s = int(r * 0.10)
    d.polygon([
        (cx, nose_y - nose_s),
        (cx - nose_s, nose_y + nose_s),
        (cx + nose_s, nose_y + nose_s),
    ], fill="#ff5577")

    # --- Angry open mouth (showing teeth) ---
    mouth_y = cy + int(r * 0.35)
    mouth_w = int(r * 0.45)
    mouth_h = int(r * 0.22)
    d.arc([cx - mouth_w, mouth_y - mouth_h, cx + mouth_w, mouth_y + mouth_h],
          start=0, end=180, fill="#220000", width=4)
    # Teeth
    tooth_w = int(mouth_w * 0.28)
    tooth_h = int(mouth_h * 0.7)
    for tx in [cx - tooth_w - 4, cx + 4]:
        d.rectangle([tx, mouth_y - 4, tx + tooth_w, mouth_y - 4 + tooth_h], fill="white")

    # --- Whiskers ---
    wy = cy + int(r * 0.10)
    wlen = int(r * 0.65)
    # Left whiskers
    for offset in [-18, 0, 18]:
        d.line([(cx - int(r * 0.15), wy + offset),
                (cx - int(r * 0.15) - wlen, wy + offset - 8)],
               fill="#ffcc88", width=2)
    # Right whiskers
    for offset in [-18, 0, 18]:
        d.line([(cx + int(r * 0.15), wy + offset),
                (cx + int(r * 0.15) + wlen, wy + offset - 8)],
               fill="#ffcc88", width=2)

    return img


def show_overlay(duration: int = 5) -> None:
    """
    Show the fullscreen alert overlay and block until it auto-dismisses.

    Call this from a dedicated thread (not the main/tray thread).
    The function returns when the overlay window is destroyed.
    """
    root = tk.Tk()

    # Fullscreen, always on top, no title bar
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg="black")

    # Capture input so clicks/keypresses don't reach apps beneath
    root.grab_set()

    # --- Main warning text ---
    warning_label = tk.Label(
        root,
        text="⚠  SYSTEM CRITICAL FAILURE  ⚠",
        font=("Courier New", 42, "bold"),
        fg="red",
        bg="black",
        pady=20,
    )
    warning_label.pack(expand=True)

    # --- Sub-message ---
    sub_label = tk.Label(
        root,
        text="CHARGE YOUR BATTERY NOW!",
        font=("Courier New", 48, "bold"),
        fg="#ff4444",
        bg="black",
        pady=10,
    )
    sub_label.pack(expand=True)

    # --- Countdown label ---
    countdown_var = tk.StringVar(value=f"Dismissing in {duration}s...")
    countdown_label = tk.Label(
        root,
        textvariable=countdown_var,
        font=("Courier New", 16),
        fg="#888888",
        bg="black",
        pady=20,
    )
    countdown_label.pack()

    # Schedule auto-dismiss after full duration
    root.after(duration * 1000, root.destroy)

    # Update countdown every second
    _schedule_countdown(root, countdown_var, duration)

    root.mainloop()  # blocks until root.destroy() is called


def _schedule_countdown(root: tk.Tk, var: tk.StringVar, remaining: int) -> None:
    """Recursively schedule countdown label updates every 1 second."""
    remaining -= 1
    if remaining <= 0:
        return
    try:
        var.set(f"Dismissing in {remaining}s...")
        root.after(1000, _schedule_countdown, root, var, remaining)
    except tk.TclError:
        pass  # window was destroyed early — ignore
