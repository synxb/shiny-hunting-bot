import subprocess
import time

import pyautogui


def get_active_window_title():
    title_getter = getattr(pyautogui, "getActiveWindowTitle", None)
    if callable(title_getter):
        return title_getter() or ""

    try:
        active_id = subprocess.check_output(
            ["xdotool", "getactivewindow"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if not active_id:
            return ""

        title = subprocess.check_output(
            ["xdotool", "getwindowname", active_id],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return title
    except (OSError, subprocess.CalledProcessError):
        return ""


def wait_for_window_title(window_title, poll_seconds=1.0):
    while window_title not in get_active_window_title():
        time.sleep(poll_seconds)
