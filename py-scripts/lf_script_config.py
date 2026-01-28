import csv
import time
import sys
import argparse
import subprocess
from pathlib import Path


def normalize_key(key: str) -> str:
    """Convert header name to --flag format"""
    flag = "--" + key.lower().replace(" ", "_")
    flag = flag.replace("packed_loss", "packet_loss")
    flag = flag.replace("pack_loss", "packet_loss")
    return flag


def prepare_config_dict(row: dict, exclude_keys: set) -> dict:
    """
    Prepare config dictionary from row.
    - No automatic comma splitting
    - Preserve quotes if present in CSV cell
    - Empty values are skipped
    """
    result = {}
    for k, v in row.items():
        if k in exclude_keys:
            continue
        # Keep original value including quotes, just strip surrounding whitespace
        v = v.rstrip() if v is not None else ""
        if not v.strip():
            continue
        result[k] = v
    return result


def apply_network_conditions(config_dict: dict, command_name: str = "./lf_create_wanlink.py"):
    """
    Build command supporting repeated parameters (when same key appears multiple times in CSV header).
    Quotes in values are preserved.
    """
    cmd = [command_name]

    # Group values by key (in case of repeated headers)
    from collections import defaultdict
    grouped = defaultdict(list)
    for key, value in config_dict.items():
        grouped[key].append(value)

    for key, values in grouped.items():
        flag = normalize_key(key)

        for value in values:
            if value.strip():  # skip truly empty after strip
                cmd.extend([flag, value])

    cmd_str = " ".join(cmd)
    print("Generated command:")
    print(f"  {cmd_str}")
    print("-" * 80)

    # Execution (comment out if you only want to preview)
    try:
        print("Executing...")
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True
        )
        print("Success!")
        if result.stdout.strip():
            print("Output:\n", result.stdout.strip())
        if result.stderr.strip():
            print("Stderr:\n", result.stderr.strip())

    except subprocess.CalledProcessError as e:
        print(f"Failed (exit {e.returncode})")
        if e.stderr:
            print("Error:\n", e.stderr.strip())
    except FileNotFoundError:
        print(f"Command not found: {command_name}")
    except Exception as e:
        print("Error:", str(e))

    print("=" * 90)


def main():
    parser = argparse.ArgumentParser(
        description="Apply network conditions from CSV - supports repeated headers and custom command"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        required=True,
        help="Path to the CSV configuration file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show more detailed output"
    )
    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.is_file():
        print(f"Error: File not found: {csv_path}", file=sys.stderr)
        return 1

    print(f"Reading: {csv_path}")
    if args.verbose:
        print(f"Full path: {csv_path.resolve()}")
    print("Press Ctrl+C to stop\n")

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Detect special columns
            sleep_header = None
            command_header = None
            for field in reader.fieldnames:
                lower = field.lower()
                if 'sleep' in lower and 'time' in lower:
                    sleep_header = field
                if lower == 'command':
                    command_header = field

            if sleep_header is None:
                print("Error: No sleep time column found")
                print("Columns:", ", ".join(reader.fieldnames))
                return 1

            if args.verbose:
                print(f"Sleep column: {sleep_header}")
                if command_header:
                    print(f"Command column: {command_header}")
                print()

            for row_num, row in enumerate(reader, 1):
                try:
                    sleep_str = (row.get(sleep_header) or "0").strip()
                    sleep_ms = int(float(sleep_str))

                    cmd_name = "./lf_create_wanlink.py"
                    if command_header and row.get(command_header):
                        cmd_name = row[command_header].strip()

                    exclude = {sleep_header}
                    if command_header:
                        exclude.add(command_header)

                    config = prepare_config_dict(row, exclude)

                    print(f"\nStep {row_num} — sleep {sleep_ms} ms — cmd: {cmd_name}")
                    apply_network_conditions(config, cmd_name)

                    if sleep_ms > 0:
                        msg = f"Waiting {sleep_ms} ms..." if args.verbose else "Waiting..."
                        print(msg, end="", flush=True)
                        time.sleep(sleep_ms / 1000.0)
                        print(" done")
                    else:
                        print("No delay")

                except ValueError as e:
                    print(f"Row {row_num}: Bad sleep value '{sleep_str}' → {e}")
                    continue
                except KeyboardInterrupt:
                    print("\nStopped by user.")
                    return 0

    except Exception as e:
        print(f"CSV error: {e}", file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
