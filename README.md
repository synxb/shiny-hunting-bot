# Shiny Hunting Automation Script

This script automates the process of Shiny Hunting in Pokémon games played on the melonDS emulator. It performs soft resets automatically and checks if the encountered Pokémon is shiny by comparing the colors of specific pixels.

## Prerequisites

Make sure you have the following Python libraries installed:

- `pyautogui`
- `opencv-python`
- `numpy`
- `keyboard`
- `pygame` (for optional gamepad recording)
- `vgamepad` (for gamepad playback/replay)

You can install these libraries using the following command:

```sh
pip install pyautogui opencv-python numpy keyboard pygame vgamepad
```

On Linux, install `xdotool` for window title/geometry fallback support:

```sh
sudo apt install xdotool
```

## Preparation

### 1. Edit the `config.json` file for your hunt:
The `config.json` file contains information about your current hunt like soft reset count, pixel coordinates, the time it takes for your chosen emulator to start after a soft reset and the time you want to take the screenshots at. To find the pixel coordinates simply input some dummy values first and let the script take an initial screenshot (after you have fine tuned the timings). From there you can open it in any image editing software to find a suitable pixel for comparison and then put these coordinates in the `config.json` file as well. The screenshot is now captured from the emulator window only, so pixel coordinates must be relative to that emulator screenshot.

`pixelCoordinates` supports both formats:
- Single point: `[x, y]`
- Multiple points: `[[x1, y1], [x2, y2], [x3, y3]]`

When multiple points are provided, the script checks all of them and treats the encounter as shiny if **any** monitored pixel differs from the reference.
Lastly edit the `emulator` section of the `config.json` file to match your emulator. NOTE: The window title of the emulator should go there. You can also override this via CLI.

### 2. Record the button sequence:
Use the `record_sequence.py` script to record the sequence of button presses needed to start the Pokémon encounter.

Example:
```sh
python src/record_sequence.py --output sequence.json
```

If `--output` is omitted, it defaults to `sequence.json`.

To record using a gamepad instead of keyboard input:
```sh
python src/record_sequence.py --gamepad --output sequence.json
```

Additional gamepad flags:
- `--gamepad`: enables gamepad recording mode
- `--gamepad-index`: selects which connected gamepad to use (default: `0`)
- `--gamepad-map`: deprecated in raw gamepad mode and ignored

Gamepad mode now records raw input events (`joybutton`, `joyhat`, `joyaxis`) and replays them as virtual gamepad input instead of keyboard key presses.

Important: re-record your sequence after updating, because old mapped gamepad recordings are not truly raw and may not match your mGBA bindings.

## Usage
### 1. Start your emulator and load your game
### 2. Run the script
```sh
python shiny_hunting.py --config config.json --sequence sequence.json --emulator "melonDS"
```
All CLI flags are optional except when you want to override defaults:
- `--config` / `-c`: path to config file (default: `config.json`)
- `--sequence` / `-s`: path to recorded sequence file (default: `sequence.json`)
- `--emulator` / `-e`: emulator window title override (if omitted, uses `emulator` from config)
- `--verbose` / `-v`: prints detailed backend/window/key event logs for troubleshooting
- `--screenshot-mode`: `window` (default) or `screen` for full-screen capture

### 3. Follow the instructions in the terminal
- Press Enter when you're ready
- The script will now automatically perform soft resets and execute the previously recorded button sequence.
- On the 1st run, a reference screenshot will be taken and on consecutive runs another one to compare. You may need to adjust the sleep timer between the screenshots depending on the game and emulator.

## Features
- **Soft Reset**: The script performs soft resets by pressing L + R + Start + Select (the keyboard keys associated with those. You may need to modify the soft reset button sequence in `soft_reset.py` depending on your game).
- **Pixel Check**: A specific pixel on the game screen is checked to determine if the Pokémon is shiny.
- **Save State**: If a shiny is found, the game is automatically saved(Again, you may need to edit the button sequence in `save_state.py` depending on your emulators keybinds).

## Important files
- **`config.json`**: Contains information about current setup like emulator title, soft reset count etc.
- **`sequence.json`**: Contains the recorded button sequence.
- **`screenshots\reference_screenshot.png`**: Reference screenshot for comparison.
- **`screenshots\current_screenshot.png`**: Current screenshot for comparison.

## Troubleshooting
- **Coordinate Error**: Ensure that `pixelCoordinates` contains either `[x, y]` or an array of `[x, y]` pairs.
- **Emulator Focus**: The script waits for the emulator window to be active. Ensure the window title is correct. The script only works if the emulator is active. If not, the button sequence execution is paused until the emulator window is active again.

## License
This project is licensed under the MIT License. See the LICENSE file for details.