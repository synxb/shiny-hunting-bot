import time
import json
import pyautogui

# Funktion zur Ausführung einer Tastensequenz


def execute_sequence(filename, window_title, verbose=False):
    with open(filename, 'r') as file:
        sequence = json.load(file)

    if verbose:
        print(f"[verbose] execute_sequence: loaded {len(sequence)} events from {filename}")

    start_time = sequence[0]['time']  # Startzeit der Sequenz

    for i, event in enumerate(sequence):
        key_name = event['name']
        if str(key_name).lower() in {'esc', 'escape'}:
            if verbose:
                print(f"[verbose] execute_sequence: skipping stop key event {event}")
            continue

        current_time = event['time']
        time_since_start = current_time - start_time
        # Verzögerung entsprechend der Zeit seit dem Start
        time.sleep(time_since_start)
        start_time = current_time  # Aktualisierung der Startzeit für die nächste Iteration

        while window_title not in (pyautogui.getActiveWindowTitle() or ""):
            time.sleep(1)

        if verbose:
            print(
                f"[verbose] execute_sequence: event {i + 1}/{len(sequence)} "
                f"type={event['event_type']} key={key_name} delay={time_since_start:.3f}s"
            )

        if event['event_type'] == 'down':
            pyautogui.keyDown(key_name)
        elif event['event_type'] == 'up':
            pyautogui.keyUp(key_name)

        # Wenn es nicht das letzte Event in der Sequenz ist, lass die vorherige Taste los
        if 0 < i < len(sequence) - 1:
            previous_event = sequence[i - 1]
            previous_key = previous_event['name']
            if str(previous_key).lower() not in {'esc', 'escape'}:
                pyautogui.keyUp(previous_key)
            if verbose:
                print(f"[verbose] execute_sequence: safety key up for {previous_key}")
        # print(event)
