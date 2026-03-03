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


def get_window_bbox(window_title):
    windows_getter = getattr(pyautogui, "getWindowsWithTitle", None)
    if callable(windows_getter):
        windows = windows_getter(window_title)
        emulator_window = next(
            (window for window in windows if window.width > 0 and window.height > 0),
            None,
        )
        if emulator_window is not None:
            return (
                emulator_window.left,
                emulator_window.top,
                emulator_window.left + emulator_window.width,
                emulator_window.top + emulator_window.height,
            )

    try:
        result = subprocess.check_output(
            ["xdotool", "search", "--name", window_title],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if not result:
            raise RuntimeError

        window_id = result.splitlines()[0].strip()
        geometry = subprocess.check_output(
            ["xdotool", "getwindowgeometry", "--shell", window_id],
            text=True,
            stderr=subprocess.DEVNULL,
        )

        values = {}
        for line in geometry.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()

        x = int(values["X"])
        y = int(values["Y"])
        width = int(values["WIDTH"])
        height = int(values["HEIGHT"])
        return (x, y, x + width, y + height)
    except (OSError, subprocess.CalledProcessError, KeyError, ValueError):
        pass

    raise RuntimeError(
        f"Could not find an open emulator window with title containing: {window_title}"
    )
