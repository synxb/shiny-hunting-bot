import cv2
import numpy as np
from PIL import ImageGrab
from window_utils import get_window_bbox


def take_screenshot(save_path, emulator_title, capture_mode="window"):
    if capture_mode == "screen":
        screenshot = ImageGrab.grab()
    else:
        bbox = get_window_bbox(emulator_title)
        screenshot = ImageGrab.grab(bbox=bbox)

    screenshot.save(save_path)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
