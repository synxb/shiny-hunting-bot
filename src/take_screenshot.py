import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab


def take_screenshot(save_path, emulator_title):
    windows = pyautogui.getWindowsWithTitle(emulator_title)
    emulator_window = next((window for window in windows if window.width > 0 and window.height > 0), None)

    if emulator_window is None:
        raise RuntimeError(f"Could not find an open emulator window with title containing: {emulator_title}")

    bbox = (
        emulator_window.left,
        emulator_window.top,
        emulator_window.left + emulator_window.width,
        emulator_window.top + emulator_window.height,
    )

    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot.save(save_path)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
