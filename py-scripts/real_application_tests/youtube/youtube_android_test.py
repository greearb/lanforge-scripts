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
import os
from pathlib import Path

LOG_FILE_PATH = os.path.abspath("youtube_test.log")
XML_OUTPUT_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    filename=LOG_FILE_PATH,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s [%(threadName)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Adb:
    def __init__(self, host="127.0.0.1", port=5037, upstream_port=None):
        """Initialize ADB clients and per-device test state."""
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

    def save_ui_xml(self, serial, stage, xml_content=None):
        """Save the latest failed UI for a device."""
        safe_serial = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(serial))
        output_path = XML_OUTPUT_DIR / f"stats_for_nerds_{safe_serial}.xml"

        try:
            if xml_content is None:
                xml_content = self.u2_sessions[serial].dump_hierarchy(
                    compressed=False
                )
            output_path.write_text(xml_content, encoding="utf-8")
            logger.info(
                "[%s] Saved %s UI XML: %s", serial, stage, output_path
            )
            return output_path
        except Exception:
            logger.exception(
                "[%s] Failed to save diagnostic UI XML for stage %s",
                serial,
                stage,
            )
            return None

    def upload_test_log(self):
        """Upload one combined log for all Android devices in this test."""
        for handler in logging.getLogger().handlers:
            handler.flush()
        try:
            with open(LOG_FILE_PATH, "rb") as log_file:
                response = requests.post(
                    f"http://{self.upstream_port}:5002/upload_youtube_log",
                    data={"device_name": "android", "device_type": "android"},
                    files={"log_file": ("youtube_test.log", log_file, "text/plain")},
                    timeout=30,
                )
            if response.status_code != 200:
                logger.error(
                    "Failed to upload Android YouTube log: "
                    "HTTP %s",
                    response.status_code,
                )
        except Exception as exc:
            logger.error("Failed to upload Android YouTube log: %s", exc)

    def get_devices(self):
        """Return list of connected ADB serials without side-effects."""
        devices = self.client.devices()
        return [d.serial for d in devices]

    def connect_devices(self):
        """Connect to devices and create uiautomator2 sessions."""
        connected_serials = []
        for serial in self.test_serials:
            try:
                device = self.client.device(serial)
                self.devices[serial] = device
                self.adb_serials[serial] = serial
                self.u2_sessions[serial] = u2.connect(serial)
                connected_serials.append(serial)
                logger.info("[%s] Device connected", serial)
            except Exception:
                logger.exception("[%s] Device connection failed", serial)
                self.devices.pop(serial, None)
                self.adb_serials.pop(serial, None)
                self.u2_sessions.pop(serial, None)
        return connected_serials

    def execute_cmd(self, device_serial, cmd):
        """Run an ADB shell command on the selected device."""
        return self.devices[device_serial].shell(cmd)

    def execute_tap(self, device_serial, x, y):
        """Tap the specified screen coordinates on a device."""
        self.devices[device_serial].input_tap(x, y)

    def execute_keyevent(self, device_serial, key_code):
        """Send an Android key event to a device."""
        self.devices[device_serial].input_keyevent(key_code)

    def open_interop_app(self, serial):
        """Open the Interop app and enter its test room."""
        d = self.u2_sessions[serial]
        d.app_start("com.candela.wecan")
        count = 0
        while "com.candela.wecan:id/enter_button" not in d.dump_hierarchy():
            time.sleep(1)
            logger.debug("[%s] Waiting for Interop app", d.serial)
            count += 1
            if count > 15:
                raise Exception(
                    f"? Interop app did not load in time for device {d.serial}"
                )
        enter_test_room = d(resourceId="com.candela.wecan:id/enter_button")
        if enter_test_room.wait(timeout=10):
            enter_test_room.click()
        else:
            raise Exception(
                f"Enter button not found in Interop app for device {d.serial}"
            )
        logger.info("[%s] Interop app opened", d.serial)

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

        def find_and_click_stats(allow_scroll=True):
            """Find and select Stats for nerds."""
            attempts = 6 if allow_scroll else 1
            for attempt in range(attempts):
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

                # Scroll only inside submenus.
                if allow_scroll and attempt < attempts - 1:
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
            logger.debug("[%s] Opening player settings", serial)
            settings_icon.click()
        else:
            logger.warning("[%s] Player menu button not found", serial)
            self.save_ui_xml(serial, "player_menu_button_not_found")
            return False

        # Step 2: Try finding Stats immediately (some versions show it directly)
        if find_and_click_stats(allow_scroll=False):
            logger.info("[%s] Stats for nerds enabled (direct path)", serial)
            return True

        # Step 3: Try clicking "More" if present (bottom sheet case)
        more_btn = d(textMatches=r"(?i)^\s*more\s*$")
        if not more_btn.exists:
            # Avoid matching "More options".
            more_btn = d(descriptionMatches=r"(?i)^\s*more\s*$")

        if more_btn.exists:
            more_btn.click()
            # Confirm that the submenu opened.
            if more_btn.wait_gone(timeout=3):
                if find_and_click_stats(allow_scroll=True):
                    logger.info("[%s] Stats for nerds enabled (More path)", serial)
                    return True
            else:
                logger.warning("[%s] More menu did not open", serial)

        # Step 4: Try clicking "Settings"
        settings_btn = d(textMatches="(?i).*settings.*")
        if settings_btn.exists:
            settings_btn.click()
            time.sleep(1)

            if find_and_click_stats(allow_scroll=True):
                logger.info("[%s] Stats for nerds enabled (Settings path)", serial)
                return True

        # Step 5: Try clicking "Advanced"
        advanced_btn = d(textMatches="(?i).*advanced.*")
        if advanced_btn.exists:
            advanced_btn.click()
            time.sleep(1)

            if find_and_click_stats(allow_scroll=True):
                logger.info("[%s] Stats for nerds enabled (Advanced path)", serial)
                return True

        logger.warning("[%s] Stats for nerds option not found", serial)
        self.save_ui_xml(serial, "option_not_found")
        return False

    def wait_for_video_ui(self, serial, timeout=40):
        """Wait until YouTube video UI is ready and skip ads if present."""
        d = self.u2_sessions[serial]
        start = time.time()

        while time.time() - start < timeout:
            if self.check_stop_signal():
                logger.info("[%s] Stop requested while waiting for video UI", serial)
                return False

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
                logger.debug("[%s] Ad playing; waiting", serial)
                time.sleep(1)
                continue

            # Check if overflow button exists (means real video UI is ready)
            if d(resourceId="com.google.android.youtube:id/player_overflow_button").exists:
                logger.info("[%s] Video UI ready", serial)
                return True

            time.sleep(1)

        logger.warning("[%s] Timed out waiting for video UI", serial)
        return False

    def send_stats_to_server(self, device_serial, stats):
        """Send one device's newly collected statistics to the report server."""
        url = f"http://{self.upstream_port}:5002/youtube_stats"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps({device_serial: stats}),
            )
            if response.status_code == 200:
                logger.debug("[%s] Stats uploaded successfully", device_serial)
            else:
                logger.warning(
                    "[%s] Stats upload failed: HTTP %s",
                    device_serial,
                    response.status_code,
                )
        except Exception as e:
            logger.warning("[%s] Stats upload error: %s", device_serial, e)

    def fetch_stats_for_nerds(self, device_serial):
        """Read and parse YouTube Stats for nerds for one device."""
        # Get the UI dump directly via uiautomator2
        d = self.u2_sessions[device_serial]
        xml_content = d.dump_hierarchy(compressed=True)

        # Parse XML
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            self.save_ui_xml(device_serial, "xml_parse_failed", xml_content)
            raise

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
        self.send_stats_to_server(device_serial, stats)

    def rotate_to_landscape(self, serial):
        """Rotate a device to landscape and verify the resulting orientation."""
        self.execute_cmd(
            serial,
            "content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0",
        )
        self.execute_cmd(
            serial,
            "content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1",
        )

        time.sleep(2)

        orientation = self.execute_cmd(
            serial, "dumpsys input | grep -i SurfaceOrientation"
        )
        logger.debug("[%s] Primary rotation result: %s", serial, orientation.strip())

        if "SurfaceOrientation: 1" in orientation:
            logger.info("[%s] Landscape rotation verified (primary method)", serial)
            return True

        self.execute_cmd(serial, "wm user-rotation free")
        time.sleep(1)
        self.execute_cmd(serial, "wm user-rotation lock 1")
        time.sleep(2)

        orientation = self.execute_cmd(
            serial, "dumpsys input | grep -i SurfaceOrientation"
        )
        logger.debug("[%s] Fallback rotation result: %s", serial, orientation.strip())

        if "SurfaceOrientation: 1" in orientation:
            logger.info("[%s] Landscape rotation verified (fallback method)", serial)
            return True

        logger.warning("[%s] Unable to verify landscape rotation", serial)
        return False

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        if self.stop_signal:
            return True
        try:
            endpoint_url = f"http://{self.upstream_port}:5002/check_stop"

            response = requests.get(endpoint_url, timeout=3)
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                if stop_signal_from_server:
                    self.stop_signal = True
                    logger.info("Stop signal received; ending test")
                else:
                    logger.debug("No stop signal received")
            return self.stop_signal
        except Exception as e:
            logger.warning("Unable to check stop signal: %s", e)
            return self.stop_signal

    def wait_or_stop(self, seconds):
        """Wait in short intervals so WebUI stop requests are handled promptly."""
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self.check_stop_signal():
                return True
            time.sleep(min(1, max(0, deadline - time.time())))
        return self.check_stop_signal()

    def run_on_device(self, serial, video_url, delay, duration, resolution):
        """Run YouTube playback and statistics collection on one device."""
        safe_serial = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(serial))
        diagnostic_xml = XML_OUTPUT_DIR / f"stats_for_nerds_{safe_serial}.xml"
        diagnostic_xml.unlink(missing_ok=True)

        try:
            logger.info(
                "[%s] Test started (delay=%ss, duration=%ss, resolution=%s)",
                serial, delay, duration, resolution or "auto",
            )
            # Force-stop YouTube app if running
            logger.info("[%s] Resetting YouTube app", serial)
            self.execute_cmd(serial, "am force-stop com.google.android.youtube")
            if self.wait_or_stop(10):
                return

            # Launch YouTube video
            logger.info("[%s] Launching video", serial)
            self.execute_cmd(
                serial,
                f"am start -a android.intent.action.VIEW -d {video_url} com.google.android.youtube",
            )
            if self.wait_or_stop(delay):
                return

            # Disable auto-rotate
            self.execute_cmd(
                serial,
                "content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0",
            )
            if self.check_stop_signal():
                return

            # Wait for video UI and try skipping ads if present.
            self.wait_for_video_ui(serial)
            if self.check_stop_signal():
                return
            if resolution:
                logger.info("[%s] Applying requested resolution %s", serial, resolution)
                self.set_resolution(serial, resolution)
                if self.check_stop_signal():
                    return

            # Rotate screen to landscape and use wm as a fallback if needed.
            self.rotate_to_landscape(serial)
            if self.check_stop_signal():
                return

            stats_enabled = self.enable_stats_for_nerds(serial)
            if not stats_enabled:
                logger.warning(
                    "[%s] Continuing playback without confirmed Stats for nerds",
                    serial,
                )
            if self.check_stop_signal():
                return

            end_time = time.time() + duration
            while time.time() < end_time and not self.check_stop_signal():
                self.fetch_stats_for_nerds(serial)
                if self.wait_or_stop(1):
                    break
        except Exception:
            logger.exception("[%s] Test failed with an unexpected error", serial)
            self.save_ui_xml(serial, "test_failed")
            raise
        finally:
            try:
                self.execute_cmd(serial, "am force-stop com.google.android.youtube")
            except Exception:
                logger.exception("[%s] Failed to stop YouTube", serial)
            try:
                self.open_interop_app(serial)
            except Exception:
                logger.exception("[%s] Failed to reopen Interop app", serial)
            logger.info("[%s] Test cleanup completed", serial)

    def run_on_multiple_devices(
        self, device_serials, video_url, delay, duration, resolution, max_workers=5
    ):
        """Run the YouTube automation concurrently on the selected devices."""
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

        logger.debug("[%s] Dumping UI hierarchy", serial)

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
                or cls in (
                    "android.support.v7.widget.RecyclerView",
                    "androidx.recyclerview.widget.RecyclerView",
                )
            ):

                container_found = True
                logger.debug("[%s] Resolution container found: %s", serial, res_id)

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

                    logger.debug(
                        "[%s] Resolution row detected: index=%s bounds=%s",
                        serial, row["adapter_index"], bounds,
                    )

                break

        if not container_found:
            logger.warning("[%s] Resolution menu container not found", serial)

        rows.sort(key=lambda r: r["adapter_index"])

        logger.debug(
            "[%s] Resolution row order: %s",
            serial, [r["adapter_index"] for r in rows],
        )

        return rows

    def click_row(self, serial, row):
        """Click the center of a validated YouTube settings row."""

        d = self.u2_sessions[serial]

        # calculate center
        cx = (row["x1"] + row["x2"]) // 2
        cy = (row["y1"] + row["y2"]) // 2

        width, height = d.window_size()

        logger.debug(
            "[%s] Clicking row: index=%s center=(%s,%s) screen=(%s,%s)",
            serial, row["adapter_index"], cx, cy, width, height,
        )

        if cx < 10 or cx > width - 10:
            logger.warning("[%s] Resolution row has invalid X coordinate: %s", serial, cx)
            return False

        if cy < 50 or cy > height - 50:
            logger.warning("[%s] Resolution row has invalid Y coordinate: %s", serial, cy)
            return False

        d.click(cx, cy)

        logger.debug("[%s] Row clicked successfully", serial)

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

        logger.debug("[%s] Capturing resolution screenshot", serial)

        try:
            with open(screenshot_file, "wb") as f:
                subprocess.run(
                    ["adb", "-s", serial, "exec-out", "screencap", "-p"],
                    stdout=f,
                    check=True
                )
        except Exception:
            logger.exception("[%s] Resolution screenshot capture failed", serial)
            return []

        img = cv2.imread(screenshot_file)

        if img is None:
            logger.error("[%s] Resolution screenshot could not be read", serial)
            return []

        logger.debug("[%s] Screenshot shape: %s", serial, img.shape)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        cv2.imwrite(f"processed_{serial}.png", thresh)

        text = pytesseract.image_to_string(thresh)

        logger.debug("[%s] OCR text: %s", serial, " ".join(text.split()))

        resolutions = re.findall(r"\d{3,4}p(?:\s*Premium)?", text)

        if len(resolutions) > 1 and resolutions[0] in resolutions[1:]:
            resolutions = resolutions[1:]

        resolutions = list(dict.fromkeys(resolutions))

        logger.info("[%s] Resolutions detected: %s", serial, resolutions)

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

        logger.info("[%s] Setting resolution to %s", serial, resolution)

        # show player controls
        for _ in range(2):
            if d(resourceId="com.google.android.youtube:id/player_overflow_button").exists:
                break
            d.click(0.5, 0.5)
            time.sleep(1)

        overflow = d(resourceId="com.google.android.youtube:id/player_overflow_button")

        if not overflow.exists:
            logger.warning("[%s] Cannot set resolution: player menu button not found", serial)
            return False

        logger.debug("[%s] Opening settings menu", serial)
        overflow.click()

        time.sleep(1)

        quality = d(textMatches="(?i).*quality.*")

        if not quality.exists:
            quality = d(descriptionMatches="(?i).*quality.*")

        if not quality.wait(timeout=5):
            logger.warning("[%s] Cannot set resolution: Quality option not found", serial)
            return False

        logger.debug("[%s] Opening Quality menu", serial)
        quality.click()

        time.sleep(1.5)

        # click last row (Advanced)
        rows = self.get_rows(serial, visible_only=True)

        if not rows:
            logger.warning("[%s] Cannot set resolution: Quality menu is empty", serial)
            return False

        logger.debug("[%s] Opening Advanced quality menu", serial)
        self.click_row(serial, rows[-1])

        time.sleep(2)

        logger.debug("[%s] Detecting resolutions using OCR", serial)

        resolutions = self.detect_resolutions_with_ocr(serial)

        rows = self.get_rows(serial, visible_only=True)

        logger.debug(
            "[%s] Resolution mapping: OCR=%s row_indexes=%s",
            serial, resolutions, [r["adapter_index"] for r in rows],
        )

        if resolution not in resolutions:
            logger.warning(
                "[%s] Requested resolution %s not detected; available=%s",
                serial, resolution, resolutions,
            )
            return False

        target_index = resolutions.index(resolution)

        if target_index >= len(rows):
            logger.warning(
                "[%s] Cannot map resolution %s: OCR index=%s, menu rows=%s",
                serial, resolution, target_index, len(rows),
            )
            return False

        logger.info("[%s] Selecting resolution %s", serial, resolution)

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
    logger.info("Test requested for devices: %s", requested)
    logger.debug("ADB devices discovered: %s", device_serials)
    missing_serials = [s for s in requested if s not in device_serials]
    if missing_serials:
        logger.warning("Requested devices not found: %s", missing_serials)
    adb_client.test_serials = test_serials
    connected_serials = adb_client.connect_devices()
    try:
        if connected_serials:
            adb_client.run_on_multiple_devices(
                connected_serials,
                video_url,
                delay,
                duration,
                resolution,
                max_workers=len(connected_serials),
            )
        else:
            logger.error("No requested Android devices are available; test not run")
    finally:
        if test_serials:
            adb_client.upload_test_log()
