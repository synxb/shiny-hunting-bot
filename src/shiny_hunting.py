import time
import json
import argparse
import cv2
import os
import numpy as np
from soft_reset import soft_reset
from sequence_execution import execute_sequence
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


def is_shiny_pixel(current_frame, reference_frame, x, y, threshold=50):
    current_pixel = current_frame[y, x]
    reference_pixel = reference_frame[y, x]

    difference = np.linalg.norm(current_pixel - reference_pixel)

    # print(f"Current pixel: {current_pixel}, Reference pixel: {
    #      reference_pixel}, Difference: {difference}")

    return difference > threshold


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
    pixel_x, pixel_y = config["pixelCoordinates"]
    pokemon_is_shiny = False
    emulator = args.emulator or config["emulator"]
    sequence_path = args.sequence
    screenshot_mode = args.screenshot_mode

    startup_time_after_reset = config["emulatorResetTimeInSeconds"]
    screenshot_time = config["screenshotTimeInSeconds"]
    print("Config loaded successfully!")
    print("Input mode: foreground-only")
    print(f"Screenshot mode: {screenshot_mode}")
    if args.verbose:
        print("[verbose] Verbose logging enabled")
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
                    if is_shiny_pixel(current_screenshot, reference_image, pixel_x, pixel_y):
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
