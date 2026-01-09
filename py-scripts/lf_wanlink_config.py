#!/usr/bin/env python3
r"""
NAME:       lf_wanlink_config.py

PURPOSE:    Read csv file which contains configuration for lf_create_wanlink.py
            and call lf_create_wanlink.py

NOTES:      The csv names uses need to match the configuration of lf_create_wanlink.py.
            The sleepTime_ms needs to get the first entry.

EXAMPLE:    # Duplicate configuration for both ends of the WANLink
            ./lf_wanlink_config.py \
                --file network_conditions.csv \
                --verbose

EXAMPLE CSV: (network_conditions.csv)

sleepTime_ms,mgr,mgr_port,wl_name,port_A,port_B,speed,latency,max_jitter,jitter_freq,drop_freq_A,drop_freq_B,log_level
2000,192.168.50.103,8080,wanlink,eth1,eth2,1014000,24,50,6,2000,3000,debug
4000,192.168.50.103,8080,wanlink,eth1,eth2,2028000,10,8,6,4000,5000,debug
5000,192.168.50.103,8080,wanlink,eth1,eth2,1014000,24,50,6,7000,8000,debug
6000,192.168.50.103,8080,wanlink,eth1,eth2,2028000,24,20,6,10000,20000,debug

add_wanpath
http://www.candelatech.com/lfcli_ug.php#add_wanpath

"""
import csv
import time
import sys
import argparse
from pathlib import Path
import subprocess
import logging
import importlib
import os

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


def apply_network_conditions(row_dict):
    """
    Implement actual network condition application logic here.
    Receives a dictionary of all parameters except the sleep time.
    """

    cmd = ["./lf_create_wanlink.py"]
    logger.info("Applying network conditions:")
    for key, value in row_dict.items():
        if not value:  # skip empty values
            continue
        logger.info(f"  {key:22} : {value}")
        # Convert key to snake_case with "--" prefix
        # 'Upload Rate' → '--upload_rate'
        # 'Upload Packet Loss' → '--upload_packet_loss'
        flag = "--" + key.lower().replace(" ", "_")
        cmd.extend([flag, value.strip()])
    # Build the full command string for display
    cmd_str = " ".join(cmd)

    # print("Generated command:")
    # print("  " + cmd_str)
    # print("-" * 60)

    logger.info(f"Generated command: {cmd_str}")

    # === Choose one of the following approaches ===

    # Option 1: Just show the command (dry-run / preview mode)
    # print("Command ready to run (dry-run mode). Uncomment subprocess below to execute.")

    # Option 2: Actually execute the command
    try:
        logger.debug("Executing command...")
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True
        )
        logger.debug("Success!")
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        if result.stderr:
            logger.info(f"Warnings/Errors: {result.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        logger.info(f"Command failed with exit code {e.returncode}")
        logger.info("Error output: {e.stderr.strip()}")
    except FileNotFoundError:
        logger.info("Error: lf_create_wanlink.py not found in PATH")
    except Exception as e:
        logger.info(f"Unexpected error while running command: {str(e)}")

    # print("-" * 60)


def validate_args(args):
    """Validate CLI arguments."""
    if args.file is None:
        logger.error("--file required")
        exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
NAME:       lf_wanlink_config.py

PURPOSE:    Read csv file which contains configuration for lf_create_wanlink.py
            and call lf_create_wanlink.py

NOTES:      The csv names uses need to match the configuration of lf_create_wanlink.py.
            The sleepTime_ms needs to get the first entry.

EXAMPLE:    # Duplicate configuration for both ends of the WANLink
            ./lf_wanlink_config.py \
                --file network_conditions.csv \
                --verbose

EXAMPLE CSV: (network_conditions.csv)

sleepTime_ms,mgr,mgr_port,wl_name,port_A,port_B,speed,latency,max_jitter,jitter_freq,drop_freq_A,drop_freq_B,log_level
2000,192.168.50.103,8080,wanlink,eth1,eth2,1014000,24,50,6,2000,3000,debug
4000,192.168.50.103,8080,wanlink,eth1,eth2,2028000,10,8,6,4000,5000,debug
5000,192.168.50.103,8080,wanlink,eth1,eth2,1014000,24,50,6,7000,8000,debug
6000,192.168.50.103,8080,wanlink,eth1,eth2,2028000,24,20,6,10000,20000,debug

add_wanpath
http://www.candelatech.com/lfcli_ug.php#add_wanpath

"""
    )

    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to the CSV configuration file (required)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show more detailed output"
    )

    # Logging Configuration
    parser.add_argument(
        '--log_level',
        default=None,
        help='Set logging level: debug | info | warning | error | critical'
    )

    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger"
    )

    # Help Summary
    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')

    return parser.parse_args()


def main():

    args = parse_args()

    help_summary = "This script creates a wanlink using the lanforge api."
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    csv_path = Path(args.file)

    if not csv_path.is_file():
        logger.error(f"Error: File not found: {csv_path} {sys.stderr}")
        return 1

    logger.info(f"Reading configuration from: {csv_path}")
    if args.verbose:
        logger.info(f"Resolved path: {csv_path.resolve()}")
    logger.info("Press Ctrl+C to stop\n")

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Auto-detect sleep time column (case-insensitive)
            sleep_header = None
            for field in reader.fieldnames:
                lower = field.lower()
                if 'sleep' in lower and 'time' in lower:
                    sleep_header = field
                    break

            if sleep_header is None:
                logger.error("Could not find sleep time column (looking for 'sleep' and 'time' in header)")
                print("Available columns:", ", ".join(reader.fieldnames))
                return 1

            if args.verbose:
                logger.info(f"Detected sleep column: '{sleep_header}'")
                print("Other parameters:", ", ".join(k for k in reader.fieldnames if k != sleep_header))

            # Process each configuration row
            for row_number, row in enumerate(reader, 1):
                try:
                    sleep_str = row[sleep_header].strip()
                    sleep_ms = int(float(sleep_str))

                    # Prepare config dict (exclude sleep, skip empty values)
                    config = {
                        k: v.strip()
                        for k, v in row.items()
                        if k != sleep_header and v.strip()
                    }

                    logger.info(f"\nStep {row_number} - Next configuration (sleep {sleep_ms} ms):")
                    apply_network_conditions(config)

                    # Sleep before next configuration
                    if sleep_ms > 0:
                        if args.verbose:
                            logger.info(f"Waiting {sleep_ms} milliseconds...")
                        else:
                            logger.info(f"Waiting {sleep_ms} milliseconds...")
                        time.sleep(sleep_ms / 1000.0)
                        logger.info(" done")
                    else:
                        logger.info("No delay (immediate next)")

                except ValueError as e:
                    logger.error(f"Error in row {row_number}: Cannot parse sleep time '{sleep_str}' → {e}")
                    continue
                except KeyboardInterrupt:
                    logger.info("\n\nStopped by user.")
                    return 0

    except Exception as e:
        logger.exception(f"Error reading CSV file: {e}")
        return 1

    logger.info("\nFinished processing all configurations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
