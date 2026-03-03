import time
import pyautogui


def soft_reset(window_title, verbose=False):
    if verbose:
        print("[verbose] soft_reset: ensuring input target is ready")
    while window_title not in (pyautogui.getActiveWindowTitle() or ""):
        time.sleep(1)

    keys = ['L', 'R', 'ENTER', 'SPACE']
    if verbose:
        print(f"[verbose] soft_reset: sending combo {keys}")
    for key in keys:
        pyautogui.keyDown(key)
    time.sleep(1)
    for key in reversed(keys):
        pyautogui.keyUp(key)
    if verbose:
        print("[verbose] soft_reset: combo sent")


if __name__ == "__main__":
    raise RuntimeError("Use shiny_hunting.py to run soft reset with proper emulator window title.")
