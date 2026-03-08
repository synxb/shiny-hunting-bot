import time
import json
import argparse
import cv2
import os
import numpy as np
from soft_reset import soft_reset
from sequence_execution import (
    execute_sequence,
    sequence_contains_gamepad_events,
    initialize_virtual_gamepad,
)
from take_screenshot import take_screenshot
from take_reference_screenshot import take_reference_screenshot
from savestate import savestate
from window_utils import wait_for_window_title


def load_config(config_path):
    with open(config_path, "r") as file:
        config = json.load(file)
    return config


def save_config(config_path, config):
    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)


def normalize_pixel_coordinates(pixel_coordinates):
    if not isinstance(pixel_coordinates, list) or not pixel_coordinates:
        raise ValueError(
            "pixelCoordinates must be [x, y] or an array of [x, y] pairs."
        )

    if (
        len(pixel_coordinates) == 2
        and all(isinstance(value, (int, float)) for value in pixel_coordinates)
    ):
        return [[int(pixel_coordinates[0]), int(pixel_coordinates[1])]]

    normalized = []
    for coord in pixel_coordinates:
        if not isinstance(coord, list) or len(coord) != 2:
            raise ValueError(
                "Each pixel coordinate must be in [x, y] format."
            )
        x_val, y_val = coord
        if not isinstance(x_val, (int, float)) or not isinstance(y_val, (int, float)):
            raise ValueError("Pixel coordinates must be numbers.")
        normalized.append([int(x_val), int(y_val)])

    if not normalized:
        raise ValueError("pixelCoordinates must contain at least one coordinate.")

    return normalized


def is_shiny_pixel(current_frame, reference_frame, pixel_coordinates, threshold=50):
    for x_val, y_val in pixel_coordinates:
        current_pixel = current_frame[y_val, x_val]
        reference_pixel = reference_frame[y_val, x_val]
        difference = np.linalg.norm(current_pixel - reference_pixel)
        if difference > threshold:
            return True

    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automate shiny hunting with configurable config/sequence and emulator."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="Path to config JSON file (default: config.json)",
    )
    parser.add_argument(
        "-s",
        "--sequence",
        default="sequence.json",
        help="Path to sequence JSON file (default: sequence.json)",
    )
    parser.add_argument(
        "-e",
        "--emulator",
        default=None,
        help="Emulator window title (overrides config value)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--screenshot-mode",
        choices=["window", "screen"],
        default="window",
        help="Screenshot area: window (default) or full screen",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    SOFT_RESET_COUNT = config["softResetCount"]
    pixel_coordinates = normalize_pixel_coordinates(config["pixelCoordinates"])
    pokemon_is_shiny = False
    emulator = args.emulator or config["emulator"]
    sequence_path = args.sequence
    screenshot_mode = args.screenshot_mode

    startup_time_after_reset = config["emulatorResetTimeInSeconds"]
    screenshot_time = config["screenshotTimeInSeconds"]
    print("Config loaded successfully!")
    print("Input mode: foreground-only")
    print(f"Screenshot mode: {screenshot_mode}")
    print(f"Pixel checks configured: {len(pixel_coordinates)}")
    if args.verbose:
        print("[verbose] Verbose logging enabled")

    uses_gamepad_sequence = sequence_contains_gamepad_events(sequence_path)
    if uses_gamepad_sequence:
        print("Detected gamepad sequence format.")
        initialize_virtual_gamepad(verbose=args.verbose)
        print("Virtual gamepad initialized.")
        print("If mGBA was already open, restart mGBA now and bind controls to the virtual Xbox 360 controller.")
        input("Press Enter after mGBA detects the virtual controller...")

    print("Record a button sequence using record_sequence.py")
    input("Press Enter, when you're ready...")

    if args.verbose:
        print("[verbose] Waiting for emulator readiness")
    wait_for_window_title(emulator)

    if not os.path.exists(r"screenshots\reference_screenshot.png"):
        if args.verbose:
            print("[verbose] No reference screenshot found, creating one")
        soft_reset(emulator, verbose=args.verbose)
        time.sleep(startup_time_after_reset)
        execute_sequence(sequence_path, emulator, verbose=args.verbose)
        time.sleep(screenshot_time)
        take_reference_screenshot(
            r"screenshots\reference_screenshot.png",
            emulator,
            capture_mode=screenshot_mode,
        )

    try:
        while not pokemon_is_shiny:

            while True:

                if args.verbose:
                    print("[verbose] Starting soft reset cycle")
                soft_reset(emulator, verbose=args.verbose)
                time.sleep(startup_time_after_reset)
                execute_sequence(sequence_path, emulator, verbose=args.verbose)

                time.sleep(screenshot_time)

                current_screenshot = take_screenshot(
                    r"screenshots\current_screenshot.png",
                    emulator,
                    capture_mode=screenshot_mode,
                )
                reference_image = cv2.imread(
                    r"screenshots\reference_screenshot.png")
                if current_screenshot is not None and reference_image is not None:
                    if is_shiny_pixel(current_screenshot, reference_image, pixel_coordinates):
                        savestate(verbose=args.verbose)
                        pokemon_is_shiny = True
                        print("Shiny Pokémon found!")
                        print(f"Soft Resets: {SOFT_RESET_COUNT}")
                        break

                # time.sleep(1)

                SOFT_RESET_COUNT += 1
                print("Current Resets:", SOFT_RESET_COUNT)
    finally:
        config["softResetCount"] = SOFT_RESET_COUNT
        save_config(args.config, config)


if __name__ == "__main__":
    main()
