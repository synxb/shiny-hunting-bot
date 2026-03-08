import time
from window_utils import wait_for_window_title
from sequence_execution import initialize_virtual_gamepad

try:
    import vgamepad as vg
except ImportError:
    vg = None


GAMEPAD_RESET_BUTTONS = [0, 1, 6, 7]
GAMEPAD_BUTTON_MAP = {
    0: "XUSB_GAMEPAD_A",
    1: "XUSB_GAMEPAD_B",
    2: "XUSB_GAMEPAD_X",
    3: "XUSB_GAMEPAD_Y",
    4: "XUSB_GAMEPAD_LEFT_SHOULDER",
    5: "XUSB_GAMEPAD_RIGHT_SHOULDER",
    6: "XUSB_GAMEPAD_BACK",
    7: "XUSB_GAMEPAD_START",
    8: "XUSB_GAMEPAD_LEFT_THUMB",
    9: "XUSB_GAMEPAD_RIGHT_THUMB",
}


def soft_reset(window_title, verbose=False):
    if vg is None:
        raise RuntimeError(
            "soft_reset gamepad mode requires vgamepad. Install it with: pip install vgamepad"
        )

    if verbose:
        print("[verbose] soft_reset: ensuring input target is ready")
    wait_for_window_title(window_title)

    gamepad = initialize_virtual_gamepad(verbose=verbose)
    buttons = [getattr(vg.XUSB_BUTTON, GAMEPAD_BUTTON_MAP[idx]) for idx in GAMEPAD_RESET_BUTTONS]

    if verbose:
        print(f"[verbose] soft_reset: sending gamepad combo buttons {GAMEPAD_RESET_BUTTONS}")

    for button in buttons:
        gamepad.press_button(button=button)
    gamepad.update()
    time.sleep(0.2)

    for button in reversed(buttons):
        gamepad.release_button(button=button)
    gamepad.update()

    if verbose:
        print("[verbose] soft_reset: combo sent")


if __name__ == "__main__":
    raise RuntimeError("Use shiny_hunting.py to run soft reset with proper emulator window title.")
