import cv2
import numpy as np
from PIL import ImageGrab
from window_utils import get_window_bbox


def take_reference_screenshot(path, emulator_title):
    bbox = get_window_bbox(emulator_title)

    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot.save(path)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
