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
import pytesseract
import cv2
import subprocess

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

    def enable_stats_for_nerds(self, serial):
        """
        Enable "Stats for nerds" in YouTube player on the given device.

        Opens the player menu and attempts to locate the option using
        multiple paths (direct, More, Settings, Advanced) with scrolling
        and regex-based matching for robustness across UI variations.

        Args:
            serial (str): Device serial number.

        Returns:
            bool: True if enabled successfully, else False.
        """
        d = self.u2_sessions[serial]
        d.click(0.2, 0.2)

        def find_and_click_stats():
            for _ in range(6):
                # Try text match
                stats_btn = d(textMatches="(?i).*stats.*nerds.*")
                if stats_btn.exists:
                    stats_btn.click()
                    return True

                # Try content description match
                stats_btn_desc = d(descriptionMatches="(?i).*stats.*nerds.*")
                if stats_btn_desc.exists:
                    stats_btn_desc.click()
                    return True

                # Scroll if possible
                d.swipe_ext("up", scale=0.7)
                time.sleep(0.8)

            return False

        # Step 1: Make sure player controls are visible
        for _ in range(2):
            if d(resourceId="com.google.android.youtube:id/player_overflow_button").exists:
                break
            d.click(0.5, 0.5)
            time.sleep(1)

        overflow = d(resourceId="com.google.android.youtube:id/player_overflow_button")
        settings_icon = d(descriptionMatches="(?i).*settings.*")

        if overflow.exists:
            overflow.click()
        elif settings_icon.exists:
            logging.info("settings icon exists, clicking it")
            settings_icon.click()
        else:
            return False

        # Step 2: Try finding Stats immediately (some versions show it directly)
        if find_and_click_stats():
            logging.info(f"[{serial}] Stats enabled (direct)")
            return True

        # Step 3: Try clicking "More" if present (bottom sheet case)
        more_btn = d(text="More")
        if not more_btn.exists:
            more_btn = d(descriptionMatches="(?i).*more.*")

        if more_btn.exists:
            more_btn.click()
            time.sleep(1)

            if find_and_click_stats():
                logging.info(f"[{serial}] Stats enabled (via More)")
                return True

        # Step 4: Try clicking "Settings"
        settings_btn = d(textMatches="(?i).*settings.*")
        if settings_btn.exists:
            settings_btn.click()
            time.sleep(1)

            if find_and_click_stats():
                logging.info(f"[{serial}] Stats enabled (via Settings)")
                return True

        # Step 5: Try clicking "Advanced"
        advanced_btn = d(textMatches="(?i).*advanced.*")
        if advanced_btn.exists:
            advanced_btn.click()
            time.sleep(1)

            if find_and_click_stats():
                logging.info(f"[{serial}] Stats enabled (via Advanced)")
                return True

        logging.info(f"[{serial}] Stats not found in any menu path")
        return False

    def wait_for_video_ui(self, serial, timeout=40):
        """Wait until YouTube video UI is ready and skip ads if present."""
        d = self.u2_sessions[serial]
        start = time.time()

        while time.time() - start < timeout:

            # If skip button exists, click it
            if d(textContains="Skip").exists:
                d(textContains="Skip").click()
                time.sleep(1)
                continue

            # If Ad label present, wait
            if (
                d(descriptionContains="Ad").exists
                or d(text="Ad").exists
                or d(textContains="Sponsored").exists
            ):
                logging.info(f"[{serial}] Ad playing, waiting...")
                time.sleep(1)
                continue

            # Check if overflow button exists (means real video UI is ready)
            if d(resourceId="com.google.android.youtube:id/player_overflow_button").exists:
                logging.info(f"[{serial}] Video UI ready")
                return True

            time.sleep(1)

        logging.info(f"[{serial}] Timeout waiting for video UI")
        return False

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
                    if unit == "kbps":
                        value /= 1000  # normalize to mbps
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

    def run_on_device(self, serial, video_url, delay, duration, resolution):
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

        # wait for video ui and try skipping ads if present
        self.wait_for_video_ui(serial)
        if resolution:
            self.set_resolution(serial, resolution)

        # Rotate screen to landscape
        self.execute_cmd(
            serial,
            "content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1",
        )

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
        self, device_serials, video_url, delay, duration, resolution, max_workers=5
    ):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.run_on_device, serial, video_url, delay, duration, resolution)
                for serial in device_serials
            ]
            # Wait for all to complete
            for future in futures:
                future.result()

    def get_rows(self, serial, visible_only=False):
        """
        Extract clickable rows from YouTube bottom sheet / RecyclerView.
        """

        d = self.u2_sessions[serial]

        logging.info(f"[{serial}] Dumping UI hierarchy")

        xml = d.dump_hierarchy(compressed=False)
        root = ET.fromstring(xml)

        # save xml for debugging
        with open(f"debug_ui_{serial}.xml", "w", encoding="utf-8") as f:
            f.write(xml)

        rows = []
        container_found = False

        for node in root.iter("node"):

            res_id = node.attrib.get("resource-id", "")
            cls = node.attrib.get("class", "")

            if (
                "bottom_sheet" in res_id
                or "recycler" in res_id
                or cls == "androidx.recyclerview.widget.RecyclerView"
            ):

                container_found = True
                logging.info(f"[{serial}] Resolution container found → {res_id}")

                for child in node.iter("node"):

                    if child.attrib.get("class") != "android.view.ViewGroup":
                        continue

                    if child.attrib.get("clickable") != "true":
                        continue

                    if visible_only and child.attrib.get("visible-to-user") != "true":
                        continue

                    bounds = child.attrib.get("bounds", "")
                    nums = re.findall(r"\d+", bounds)

                    if len(nums) != 4:
                        continue

                    x1, y1, x2, y2 = map(int, nums)

                    # filter small rows
                    if (y2 - y1) < 60:
                        continue

                    row = {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "adapter_index": int(child.attrib.get("index", -1))
                    }

                    rows.append(row)

                    logging.info(
                        f"[{serial}] Row detected index={row['adapter_index']} bounds={bounds}"
                    )

                break

        if not container_found:
            logging.warning(f"[{serial}] No RecyclerView / bottom sheet container found")

        rows.sort(key=lambda r: r["adapter_index"])

        logging.info(f"[{serial}] Final row order: {[r['adapter_index'] for r in rows]}")

        return rows

    def click_row(self, serial, row):

        d = self.u2_sessions[serial]

        # calculate center
        cx = (row["x1"] + row["x2"]) // 2
        cy = (row["y1"] + row["y2"]) // 2

        width, height = d.window_size()

        logging.info(
            f"[{serial}] Clicking row index={row['adapter_index']} center=({cx},{cy}) screen=({width},{height})"
        )

        if cx < 10 or cx > width - 10:
            logging.warning(f"[{serial}] Invalid click X")
            return False

        if cy < 50 or cy > height - 50:
            logging.warning(f"[{serial}] Invalid click Y")
            return False

        d.click(cx, cy)

        logging.info(f"[{serial}] Row clicked successfully")

        return True

    def detect_resolutions_with_ocr(self, serial):
        """
        Capture device screen and use OCR to extract available video resolutions.

        Args:
            serial (str): Device serial number.

        Returns:
            list: List of detected resolution strings (e.g., ["144p", "360p", "720p"]).
                Returns an empty list if screenshot capture or OCR fails.

        Notes:
            - Requires Tesseract OCR to be installed and accessible.
            - OCR accuracy depends on screen clarity and preprocessing.
            - Assumes resolution labels are visible on the screen at capture time.
        """
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

        screenshot_file = f"resolution_screen_{serial}.png"

        logging.info(f"[{serial}] Capturing screenshot")

        try:
            with open(screenshot_file, "wb") as f:
                subprocess.run(
                    ["adb", "-s", serial, "exec-out", "screencap", "-p"],
                    stdout=f,
                    check=True
                )
        except Exception as e:
            logging.error(f"[{serial}] Screenshot capture failed: {e}")
            return []

        img = cv2.imread(screenshot_file)

        if img is None:
            logging.error(f"[{serial}] Screenshot failed")
            return []

        logging.info(f"[{serial}] Screenshot shape {img.shape}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        cv2.imwrite(f"processed_{serial}.png", thresh)

        text = pytesseract.image_to_string(thresh)

        logging.info(f"[{serial}] OCR text:\n{text}")

        resolutions = re.findall(r"\d{3,4}p(?:\s*Premium)?", text)

        if len(resolutions) > 1 and resolutions[0] in resolutions[1:]:
            resolutions = resolutions[1:]

        resolutions = list(dict.fromkeys(resolutions))

        logging.info(f"[{serial}] OCR resolutions detected → {resolutions}")

        return resolutions

    def set_resolution(self, serial, resolution):
        """
        Set the video playback resolution on YouTube.

        Navigates through the YouTube player settings menu, opens the quality
        options, selects the advanced menu, and chooses the desired resolution
        using OCR-based detection and row mapping.

        Args:
            serial (str): Device serial number.
            resolution (str): Desired resolution (e.g., "720p", "1080p").

        Returns:
            bool: True if resolution was successfully set, False otherwise.
        """

        d = self.u2_sessions[serial]

        logging.info(f"[{serial}] ===== Setting resolution {resolution} =====")

        # show player controls
        for _ in range(2):
            if d(resourceId="com.google.android.youtube:id/player_overflow_button").exists:
                break
            d.click(0.5, 0.5)
            time.sleep(1)

        overflow = d(resourceId="com.google.android.youtube:id/player_overflow_button")

        if not overflow.exists:
            logging.warning(f"[{serial}] Overflow button not found")
            return False

        logging.info(f"[{serial}] Opening settings menu")
        overflow.click()

        time.sleep(1)

        quality = d(textMatches="(?i).*quality.*")

        if not quality.exists:
            quality = d(descriptionMatches="(?i).*quality.*")

        if not quality.wait(timeout=5):
            logging.warning(f"[{serial}] Quality option not found")
            return False

        logging.info(f"[{serial}] Opening Quality menu")
        quality.click()

        time.sleep(1.5)

        # click last row (Advanced)
        rows = self.get_rows(serial, visible_only=True)

        if not rows:
            logging.warning(f"[{serial}] No rows found in Quality menu")
            return False

        logging.info(f"[{serial}] Clicking last row (assumed Advanced)")
        self.click_row(serial, rows[-1])

        time.sleep(2)

        logging.info(f"[{serial}] Detecting resolutions using OCR")

        resolutions = self.detect_resolutions_with_ocr(serial)

        rows = self.get_rows(serial, visible_only=True)

        logging.info(
            f"[{serial}] Mapping resolution → rows | OCR={resolutions} rows={[r['adapter_index'] for r in rows]}"
        )

        if resolution not in resolutions:
            logging.warning(f"[{serial}] Requested resolution {resolution} not found")
            return False

        target_index = resolutions.index(resolution)

        if target_index >= len(rows):
            logging.warning(
                f"[{serial}] OCR index {target_index} exceeds row count {len(rows)}"
            )
            return False

        logging.info(f"[{serial}] Clicking resolution {resolution}")

        self.click_row(serial, rows[target_index])

        return True


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
    parser.add_argument("--resolution", type=str, help="give the desired resolution")

    args = parser.parse_args()

    video_url = args.url  # https://youtu.be/ID2zk0M5U7s?si=hECC-d8tSb5JdiTd
    duration = int(args.duration) * 60  # minutes to seconds
    resolution = args.resolution
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
            resolution,
            max_workers=len(test_serials),
        )
