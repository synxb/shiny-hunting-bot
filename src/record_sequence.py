import json
import argparse
import time
import keyboard
from keyboard import record

try:
    import pygame
except ImportError:
    pygame = None

AXIS_CHANGE_EPSILON = 0.02

def parse_args():
    parser = argparse.ArgumentParser(
        description="Record a key sequence and save it as JSON."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="sequence.json",
        help="Output path for sequence JSON (default: sequence.json)",
    )
    parser.add_argument(
        "--gamepad",
        action="store_true",
        help="Record using a gamepad instead of keyboard input.",
    )
    parser.add_argument(
        "--gamepad-index",
        type=int,
        default=0,
        help="Gamepad index to use with --gamepad (default: 0).",
    )
    parser.add_argument(
        "--gamepad-map",
        help=(
            "Deprecated: no longer used in raw gamepad recording mode."
        ),
    )
    return parser.parse_args()


def record_sequence(output_path):
    print("Press key sequence to initiate the battle (ESC to stop)")
    recorded = record(until='esc')
    sequence = [{'name': e.name, 'event_type': e.event_type, 'time': e.time}
                for e in recorded]
    with open(output_path, 'w') as f:
        json.dump(sequence, f)
    print(f"Sequence recorded and saved to {output_path}.")


def record_gamepad_sequence(output_path, gamepad_index=0, mapping_path=None):
    if pygame is None:
        raise RuntimeError(
            "Gamepad recording requires pygame. Install it with: pip install pygame"
        )

    if mapping_path:
        print("Warning: --gamepad-map is ignored in raw gamepad recording mode.")

    pygame.init()
    pygame.joystick.init()

    try:
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            raise RuntimeError("No gamepad detected.")
        if gamepad_index < 0 or gamepad_index >= joystick_count:
            raise RuntimeError(
                f"Gamepad index {gamepad_index} is out of range. "
                f"Detected devices: {joystick_count}."
            )

        joystick = pygame.joystick.Joystick(gamepad_index)
        joystick.init()

        print(f"Using gamepad {gamepad_index}: {joystick.get_name()}")
        print("Recording raw gamepad inputs (ESC on keyboard to stop)")

        sequence = []
        start_time = time.time()
        axis_values = {}

        for axis_idx in range(joystick.get_numaxes()):
            axis_values[axis_idx] = joystick.get_axis(axis_idx)

        def append_event(payload):
            sequence.append({
                'input_device': 'gamepad',
                'time': start_time + (time.time() - start_time),
                **payload,
            })

        while True:
            if keyboard.is_pressed('esc'):
                break

            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    append_event({
                        'raw_type': 'joybutton',
                        'button': int(event.button),
                        'event_type': 'down',
                    })
                elif event.type == pygame.JOYBUTTONUP:
                    append_event({
                        'raw_type': 'joybutton',
                        'button': int(event.button),
                        'event_type': 'up',
                    })
                elif event.type == pygame.JOYHATMOTION:
                    x_val, y_val = event.value
                    append_event({
                        'raw_type': 'joyhat',
                        'hat': int(event.hat),
                        'value': [int(x_val), int(y_val)],
                        'event_type': 'motion',
                    })
                elif event.type == pygame.JOYAXISMOTION:
                    axis_idx = int(event.axis)
                    axis_val = float(event.value)
                    previous_val = axis_values.get(axis_idx, 0.0)
                    if abs(axis_val - previous_val) >= AXIS_CHANGE_EPSILON:
                        axis_values[axis_idx] = axis_val
                        append_event({
                            'raw_type': 'joyaxis',
                            'axis': axis_idx,
                            'value': axis_val,
                            'event_type': 'motion',
                        })

            time.sleep(0.005)

        if not sequence:
            print("No gamepad inputs were recorded.")
            return

        with open(output_path, 'w') as f:
            json.dump(sequence, f)

        print(f"Sequence recorded and saved to {output_path}.")
    finally:
        pygame.joystick.quit()
        pygame.quit()


if __name__ == "__main__":
    args = parse_args()
    if args.gamepad:
        record_gamepad_sequence(
            args.output,
            gamepad_index=args.gamepad_index,
            mapping_path=args.gamepad_map,
        )
    else:
        record_sequence(args.output)
