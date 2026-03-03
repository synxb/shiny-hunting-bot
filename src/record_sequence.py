import json
import argparse
from keyboard import record

# Funktion zum Aufzeichnen der Tastensequenz


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
    return parser.parse_args()


def record_sequence(output_path):
    print("Press key sequence to initiate the battle (ESC to stop)")
    recorded = record(until='esc')
    sequence = [{'name': e.name, 'event_type': e.event_type, 'time': e.time}
                for e in recorded]
    with open(output_path, 'w') as f:
        json.dump(sequence, f)
    print(f"Sequence recorded and saved to {output_path}.")


if __name__ == "__main__":
    args = parse_args()
    record_sequence(args.output)
