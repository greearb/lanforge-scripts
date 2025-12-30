#!/usr/bin/env python3
from ppadb.client import Client as AdbClient
import uiautomator2 as u2
import xml.etree.ElementTree as ET
import re
import time
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import logging

logging.basicConfig(
    filename='youtube_test.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class Adb:
    def __init__(self, host="127.0.0.1", port=5037, upstream_port=None):
        self.host = host
        self.port = port
        self.client = AdbClient(host=self.host, port=self.port)
        self.devices = {}
        self.adb_serials = {}
        self.u2_sessions = {}
        self.stats = {}
        self.upstream_port = upstream_port
        self.test_serials = []
        self.stop_signal = False

    def get_devices(self):
        """Return list of connected ADB serials without side-effects."""
        devices = self.client.devices()
        return [d.serial for d in devices]

    def connect_devices(self):
        """Connect to devices and create uiautomator2 sessions."""
        for serial in self.test_serials:
            try:
                device = self.client.device(serial)
                self.devices[serial] = device
                self.adb_serials[serial] = serial
                self.u2_sessions[serial] = u2.connect(serial)
                logging.info(f"Connected to device: {serial}")
            except Exception as e:
                logging.info(f"Failed to connect to device {serial}: {e}")

    def execute_cmd(self, device_serial, cmd):
        return self.devices[device_serial].shell(cmd)

    def execute_tap(self, device_serial, x, y):
        self.devices[device_serial].input_tap(x, y)

    def execute_keyevent(self, device_serial, key_code):
        self.devices[device_serial].input_keyevent(key_code)

    def open_interop_app(self, serial):
        d = self.u2_sessions[serial]
        d.app_start("com.candela.wecan")
        count = 0
        while "com.candela.wecan:id/enter_button" not in d.dump_hierarchy():
            time.sleep(1)
            logging.info(f"Waiting for Interop app to load on device {d.serial}...")
            count += 1
            if count > 15:
                raise Exception(
                    f"❌ Interop app did not load in time for device {d.serial}"
                )
        enter_test_room = d(resourceId="com.candela.wecan:id/enter_button")
        if enter_test_room.wait(timeout=10):
            enter_test_room.click()
        else:
            raise Exception(
                f"Enter button not found in Interop app for device {d.serial}"
            )
        logging.info(f"Opened Interop app on device {d.serial}")

    def enable_stats_for_nerds(self, device_serial):
        """
        Enable 'Stats for nerds' while a video is playing.
        """

        d = self.u2_sessions[device_serial]

        # Step 1: Open the overflow menu (⋮)
        count = 0
        while (
            "com.google.android.youtube:id/player_overflow_button"
            not in d.dump_hierarchy()
        ):
            time.sleep(1)
            logging.info(
                f"Waiting for overflow button to appear... for serial: {device_serial}"
            )
            count += 1
            if count > 15:
                logging.info(
                    f"Timeout waiting for overflow button. for serial: {device_serial}"
                )
                return False
        btn = d(resourceId="com.google.android.youtube:id/player_overflow_button")
        if btn.wait(timeout=10):  # waits up to 10 seconds for the element to appear
            btn.click()
            logging.info(f"☰ Overflow menu opened. for serial: {device_serial}")
        time.sleep(1)

        # Step 2: Click "More options" inside overflow
        count = 0
        while "More " not in d.dump_hierarchy():
            time.sleep(1)
            logging.info(
                f"Waiting for 'More' option to appear... for serial: {device_serial}"
            )
            count += 1
            if count > 15:
                logging.info(
                    f"Timeout waiting for 'More' option. for serial: {device_serial}"
                )
                return False
        more_button = d(description="More ")
        if more_button.wait(timeout=10):
            more_button.click()
            logging.info(f"➡️ Entered More submenu. for serial: {device_serial}")

        time.sleep(2)

        d.swipe_ext("up", scale=0.6)
        time.sleep(3)
        count = 0
        while "Stats for nerds " not in d.dump_hierarchy():
            time.sleep(1)
            logging.info(
                f"Waiting for 'Stats for nerds' option to appear... for serial: {device_serial}"
            )
            count += 1
            if count > 15:
                logging.info(
                    f"Timeout waiting for 'Stats for nerds' option. for serial: {device_serial}"
                )
                return False
        stats_button = d(description="Stats for nerds ")
        if stats_button.wait(timeout=10):
            stats_button.click()
            logging.info(f"✅ Stats for nerds enabled. for serial: {device_serial}")
            return True

    def skip_ads(self, serial):
        """Continuously check and skip YouTube ads if possible."""
        try:
            d = self.u2_sessions[serial]
            while True:
                # Look for the "Skip Ads" button
                if d(textContains="Skip").exists:
                    d(textContains="Skip").click()
                    logging.info(f"[{serial}] Skipped ad")
                    break
                # Some ads say "Ad" in the title, so wait for them to finish
                if (
                    d(descriptionContains="Ad").exists
                    or d(text="Ad").exists
                    or d(text="sponsored").exists
                    or d(text="Sponsored").exists
                ):
                    logging.info(f"[{serial}] Ad playing, waiting...")
                else:
                    # No ad detected → break
                    break
                time.sleep(0.5)
        except Exception as e:
            logging.info(f"[{serial}] Ad skip check failed: {e}")

    def send_stats_to_server(self):
        url = f"http://{self.upstream_port}:5002/youtube_stats"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, data=json.dumps(self.stats))
            if response.status_code == 200:
                logging.info("Stats sent successfully.")
            else:
                logging.info(
                    f"Failed to send stats. Status code: {response.status_code}"
                )
        except Exception as e:
            logging.info(f"Error sending stats: {e}")

    def fetch_stats_for_nerds(self, device_serial):
        # Get the UI dump directly via uiautomator2
        d = self.u2_sessions[device_serial]
        xml_content = d.dump_hierarchy(compressed=True)

        # Parse XML
        root = ET.fromstring(xml_content)

        raw_stats = ""
        for node in root.iter("node"):
            text = node.attrib.get("text", "")
            if text:
                raw_stats += text + " "

        stats = {}
        patterns = {
            "Device Serial": r"Device:\s*(.*?)\s*CPN:",
            "video_format": r"Video format:\s*(.*?)\s*Audio format:",
            "audio_format": r"Audio format:\s*(.*?)\s*Volume/Normalized:",
            "bandwidth (kbps)": r"Bandwidth:\s*([0-9.]+)\s*(kbps|mbps)",
            "readahead (s)": r"Readahead:\s*([0-9.]+)\s*s",
            "viewport": r"Viewport:\s*(.*?)\s*Dropped frames:",
            "dropped_frames": r"Dropped frames:\s*([0-9]+)\s*/\s*([0-9]+)",
        }

        stats = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_stats, re.IGNORECASE | re.DOTALL)
            if match:
                if key == "dropped_frames":
                    stats["DroppedFrames"] = int(match.group(1))
                    stats["TotalFrames"] = int(match.group(2))

                elif key == "bandwidth (kbps)":
                    value = float(match.group(1))
                    unit = match.group(2).lower()
                    if unit == "mbps":
                        value *= 1000  # normalize to kbps
                    stats[key] = round(value, 2)

                elif key == "readahead (s)":
                    stats["BufferHealth"] = float(match.group(1))

                elif key == "viewport":
                    value = match.group(1).strip()
                    stats["Viewport"] = value

                else:
                    value = match.group(1).strip()
                    # Clean extras
                    if key == "video_format":
                        value = re.sub(r"\[.*?\]", "", value).strip()
                        stats["CurrentRes"] = value
                    if key == "volume_normalized":
                        value = re.sub(r"\[Copy debug info\]", "", value).strip()
                        stats[key] = value

        stats["Timestamp"] = datetime.now().strftime("%H:%M:%S")
        self.stats[device_serial] = stats
        self.send_stats_to_server()

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"http://{self.upstream_port}:5002/check_stop"

            response = requests.get(endpoint_url)
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                if stop_signal_from_server:
                    self.stop_signal = True
                    logging.info(
                        "Stop signal received from the server. Exiting the loop."
                    )
                else:

                    logging.info("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            logging.info(f"Error checking stop signal: {e}")

    def run_on_device(self, serial, video_url, delay, duration):
        # Force-stop YouTube app if running
        self.execute_cmd(serial, "am force-stop com.google.android.youtube")
        time.sleep(10)

        # Launch YouTube video
        self.execute_cmd(
            serial,
            f"am start -a android.intent.action.VIEW -d {video_url} com.google.android.youtube",
        )
        time.sleep(delay)

        # Disable auto-rotate
        self.execute_cmd(
            serial,
            "content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0",
        )

        # Rotate screen to landscape
        self.execute_cmd(
            serial,
            "content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1",
        )

        # Try skipping ads if present
        self.skip_ads(serial)

        # Enable stats
        self.enable_stats_for_nerds(serial)

        start_time = time.time()
        end_time = start_time + duration  # duration is in seconds

        while time.time() < end_time:
            self.fetch_stats_for_nerds(serial)
            time.sleep(1)  # control polling frequency
            if self.check_stop_signal():
                break
        self.execute_cmd(serial, "am force-stop com.google.android.youtube")
        self.open_interop_app(serial)
        logging.info(f"[{serial}] Test completed or stopped.")

    def run_on_multiple_devices(
        self, device_serials, video_url, delay, duration, max_workers=5
    ):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.run_on_device, serial, video_url, delay, duration)
                for serial in device_serials
            ]
            # Wait for all to complete
            for future in futures:
                future.result()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Play YouTube video automation with ad skipping"
    )
    parser.add_argument(
        "--url", type=str, required=True, help="YouTube video URL to play"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Video play duration in Minutes"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=0,
        help="Delay before starting video playback (in seconds)",
    )
    parser.add_argument(
        "--devices",
        type=str,
        required=True,
        help="Comma-separated list of device serials to run the test on",
    )
    parser.add_argument(
        "--upstream_port",
        type=str,
        required=True,
        help="Upstream port for LANforge",
    )
    args = parser.parse_args()

    video_url = args.url  # https://youtu.be/ID2zk0M5U7s?si=hECC-d8tSb5JdiTd
    duration = int(args.duration) * 60  # minutes to seconds
    delay = args.delay
    adb_client = Adb(upstream_port=args.upstream_port)
    device_serials = adb_client.get_devices()
    requested = args.devices.split(",")
    test_serials = [s for s in requested if s in device_serials]
    logging.info(f"Running test on devices: {test_serials}")
    logging.info(f"All connected devices: {device_serials}")
    adb_client.test_serials = test_serials
    adb_client.connect_devices()
    if test_serials:
        adb_client.run_on_multiple_devices(
            test_serials,
            video_url,
            delay,
            duration,
            max_workers=len(test_serials),
        )
