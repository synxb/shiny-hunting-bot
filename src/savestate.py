import time
import pyautogui


def savestate(verbose=False):
    keys = ['SHIFT', 'F1']
    if verbose:
        print(f"[verbose] savestate: sending combo {keys}")
    for key in keys:
        pyautogui.keyDown(key)
    time.sleep(1)
    for key in reversed(keys):
        pyautogui.keyUp(key)


if __name__ == "__main__":
    raise RuntimeError("Use shiny_hunting.py to run save state.")
