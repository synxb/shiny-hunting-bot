import time
import json
import pyautogui
from window_utils import wait_for_window_title

try:
    import vgamepad as vg
except ImportError:
    vg = None


_VIRTUAL_GAMEPAD_SINGLETON = None
_VIRTUAL_GAMEPAD_INITIALIZED = False


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

AXIS_INT16_MIN = -32768
AXIS_INT16_MAX = 32767


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def _float_axis_to_int16(value):
    clamped = _clamp(float(value), -1.0, 1.0)
    if clamped >= 0:
        return int(round(clamped * AXIS_INT16_MAX))
    return int(round(clamped * -AXIS_INT16_MIN))


def _float_trigger_to_uint8(value):
    clamped = _clamp(float(value), -1.0, 1.0)
    normalized = (clamped + 1.0) / 2.0
    return int(round(normalized * 255.0))


def _split_hat_to_buttons(hat_value):
    x_val = 0
    y_val = 0
    if isinstance(hat_value, (list, tuple)) and len(hat_value) == 2:
        x_val = int(hat_value[0])
        y_val = int(hat_value[1])
    return {
        "XUSB_GAMEPAD_DPAD_UP": y_val > 0,
        "XUSB_GAMEPAD_DPAD_DOWN": y_val < 0,
        "XUSB_GAMEPAD_DPAD_LEFT": x_val < 0,
        "XUSB_GAMEPAD_DPAD_RIGHT": x_val > 0,
    }


def sequence_contains_gamepad_events(filename):
    with open(filename, 'r') as file:
        sequence = json.load(file)
    return any(event.get('input_device') == 'gamepad' for event in sequence)


def initialize_virtual_gamepad(verbose=False):
    global _VIRTUAL_GAMEPAD_SINGLETON
    global _VIRTUAL_GAMEPAD_INITIALIZED

    if vg is None:
        raise RuntimeError(
            "Gamepad playback requires vgamepad. Install it with: pip install vgamepad"
        )

    if _VIRTUAL_GAMEPAD_SINGLETON is None:
        if verbose:
            print("[verbose] sequence_execution: creating persistent virtual gamepad")
        _VIRTUAL_GAMEPAD_SINGLETON = vg.VX360Gamepad()

    if not _VIRTUAL_GAMEPAD_INITIALIZED:
        _VIRTUAL_GAMEPAD_SINGLETON.update()
        time.sleep(0.2)
        _VIRTUAL_GAMEPAD_INITIALIZED = True
        if verbose:
            print("[verbose] sequence_execution: virtual gamepad initialized")

    return _VIRTUAL_GAMEPAD_SINGLETON

# Funktion zur Ausführung einer Tastensequenz


def execute_sequence(filename, window_title, verbose=False):
    with open(filename, 'r') as file:
        sequence = json.load(file)

    if not sequence:
        if verbose:
            print(f"[verbose] execute_sequence: sequence file {filename} is empty")
        return

    if verbose:
        print(f"[verbose] execute_sequence: loaded {len(sequence)} events from {filename}")

    start_time = sequence[0]['time']  # Startzeit der Sequenz
    virtual_gamepad = None
    pressed_keyboard_keys = set()
    hat_states = {}
    raw_axis_state = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: -1.0,
        5: -1.0,
    }

    def ensure_virtual_gamepad():
        nonlocal virtual_gamepad
        virtual_gamepad = initialize_virtual_gamepad(verbose=verbose)
        return virtual_gamepad

    def apply_axis_state(gamepad):
        gamepad.left_joystick(
            x_value=_float_axis_to_int16(raw_axis_state.get(0, 0.0)),
            y_value=_float_axis_to_int16(raw_axis_state.get(1, 0.0)),
        )
        gamepad.right_joystick(
            x_value=_float_axis_to_int16(raw_axis_state.get(2, 0.0)),
            y_value=_float_axis_to_int16(raw_axis_state.get(3, 0.0)),
        )
        gamepad.left_trigger(value=_float_trigger_to_uint8(raw_axis_state.get(4, -1.0)))
        gamepad.right_trigger(value=_float_trigger_to_uint8(raw_axis_state.get(5, -1.0)))

    def safe_key_up(key_name):
        try:
            pyautogui.keyUp(key_name)
        except Exception:
            pass

    modifier_fallback_keys = {
        'ctrl', 'ctrlleft', 'ctrlright',
        'shift', 'shiftleft', 'shiftright',
        'alt', 'altleft', 'altright',
        'win', 'winleft', 'winright',
        'command', 'option',
    }

    try:
        for i, event in enumerate(sequence):
            input_device = event.get('input_device', 'keyboard')

            current_time = event['time']
            time_since_start = current_time - start_time
            # Verzögerung entsprechend der Zeit seit dem Start
            time.sleep(time_since_start)
            start_time = current_time  # Aktualisierung der Startzeit für die nächste Iteration

            if input_device == 'gamepad':
                gamepad = ensure_virtual_gamepad()
                raw_type = event.get('raw_type')

                if raw_type == 'joybutton':
                    button_index = event.get('button')
                    event_type = event.get('event_type')
                    button_name = GAMEPAD_BUTTON_MAP.get(button_index)
                    if button_name and event_type in {'down', 'up'}:
                        button = getattr(vg.XUSB_BUTTON, button_name)
                        if event_type == 'down':
                            gamepad.press_button(button=button)
                        else:
                            gamepad.release_button(button=button)
                        gamepad.update()
                    elif verbose:
                        print(f"[verbose] execute_sequence: unsupported raw joybutton event {event}")

                elif raw_type == 'joyhat':
                    hat_index = int(event.get('hat', 0))
                    new_hat_state = _split_hat_to_buttons(event.get('value', [0, 0]))
                    previous_hat_state = hat_states.get(hat_index, {
                        "XUSB_GAMEPAD_DPAD_UP": False,
                        "XUSB_GAMEPAD_DPAD_DOWN": False,
                        "XUSB_GAMEPAD_DPAD_LEFT": False,
                        "XUSB_GAMEPAD_DPAD_RIGHT": False,
                    })
                    for button_name, is_pressed in new_hat_state.items():
                        was_pressed = previous_hat_state.get(button_name, False)
                        if is_pressed == was_pressed:
                            continue
                        button = getattr(vg.XUSB_BUTTON, button_name)
                        if is_pressed:
                            gamepad.press_button(button=button)
                        else:
                            gamepad.release_button(button=button)
                    hat_states[hat_index] = new_hat_state
                    gamepad.update()

                elif raw_type == 'joyaxis':
                    axis_index = int(event.get('axis', -1))
                    axis_value = float(event.get('value', 0.0))
                    raw_axis_state[axis_index] = axis_value
                    apply_axis_state(gamepad)
                    gamepad.update()

                elif 'control' in event:
                    control = event.get('control')
                    event_type = event.get('event_type')
                    if isinstance(control, str) and control.startswith('button_') and event_type in {'down', 'up'}:
                        try:
                            button_index = int(control.split('_', 1)[1])
                        except (ValueError, IndexError):
                            button_index = -1
                        button_name = GAMEPAD_BUTTON_MAP.get(button_index)
                        if button_name:
                            button = getattr(vg.XUSB_BUTTON, button_name)
                            if event_type == 'down':
                                gamepad.press_button(button=button)
                            else:
                                gamepad.release_button(button=button)
                            gamepad.update()
                    elif isinstance(control, str) and control.startswith('hat_') and event_type in {'down', 'up'}:
                        parts = control.split('_')
                        if len(parts) == 3:
                            _, hat_index_str, direction = parts
                            try:
                                hat_index = int(hat_index_str)
                            except ValueError:
                                hat_index = 0
                            x_val = 0
                            y_val = 0
                            if direction == 'up':
                                y_val = 1 if event_type == 'down' else 0
                            elif direction == 'down':
                                y_val = -1 if event_type == 'down' else 0
                            elif direction == 'left':
                                x_val = -1 if event_type == 'down' else 0
                            elif direction == 'right':
                                x_val = 1 if event_type == 'down' else 0
                            new_hat_state = _split_hat_to_buttons([x_val, y_val])
                            previous_hat_state = hat_states.get(hat_index, {
                                "XUSB_GAMEPAD_DPAD_UP": False,
                                "XUSB_GAMEPAD_DPAD_DOWN": False,
                                "XUSB_GAMEPAD_DPAD_LEFT": False,
                                "XUSB_GAMEPAD_DPAD_RIGHT": False,
                            })
                            for button_name, is_pressed in new_hat_state.items():
                                was_pressed = previous_hat_state.get(button_name, False)
                                if is_pressed == was_pressed:
                                    continue
                                button = getattr(vg.XUSB_BUTTON, button_name)
                                if is_pressed:
                                    gamepad.press_button(button=button)
                                else:
                                    gamepad.release_button(button=button)
                            hat_states[hat_index] = new_hat_state
                            gamepad.update()

                elif verbose:
                    print(f"[verbose] execute_sequence: unsupported gamepad event {event}")

                if verbose:
                    print(
                        f"[verbose] execute_sequence: event {i + 1}/{len(sequence)} "
                        f"gamepad_event={event} delay={time_since_start:.3f}s"
                    )
                continue

            key_name = event.get('name')
            if key_name is None:
                if verbose:
                    print(f"[verbose] execute_sequence: skipping invalid keyboard event {event}")
                continue

            if str(key_name).lower() in {'esc', 'escape'}:
                if verbose:
                    print(f"[verbose] execute_sequence: skipping stop key event {event}")
                continue

            wait_for_window_title(window_title)

            if verbose:
                print(
                    f"[verbose] execute_sequence: event {i + 1}/{len(sequence)} "
                    f"type={event['event_type']} key={key_name} delay={time_since_start:.3f}s"
                )

            if event['event_type'] == 'down':
                pyautogui.keyDown(key_name)
                pressed_keyboard_keys.add(str(key_name).lower())
            elif event['event_type'] == 'up':
                pyautogui.keyUp(key_name)
                pressed_keyboard_keys.discard(str(key_name).lower())
    finally:
        for key_name in list(pressed_keyboard_keys):
            safe_key_up(key_name)
        for key_name in modifier_fallback_keys:
            safe_key_up(key_name)
