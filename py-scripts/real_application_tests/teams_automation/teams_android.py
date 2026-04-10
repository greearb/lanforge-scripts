import uiautomator2 as u2
import time
from ppadb.client import Client as AdbClient
import xml.etree.ElementTree as ET
from datetime import datetime
import argparse
import pytz
import requests
import logging
import os
import sys


class TeamsAndroid:
    def __init__(
        self,
        host="127.0.0.1",
        port=5037,
        upstream_port=None,
        meet_link=None,
        participant_name=None,
    ):
        self.host = host
        self.port = port
        self.client = AdbClient(host=self.host, port=self.port)
        self.serial = None
        self.d = None
        self.upstream_port = upstream_port
        self.stop_signal = False
        self.audio = True
        self.video = True
        self.meet_link = meet_link
        self.start_time = None
        self.end_time = None
        self.tz = pytz.timezone("Asia/Kolkata")
        self.base_url = f"http://{self.upstream_port}:5005"
        self.participant_name = participant_name

        os.makedirs(f"{os.getcwd()}/ms_teams_mobile_logs", exist_ok=True)

        # Configure the logging system
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    f"{os.getcwd()}/ms_teams_mobile_logs/{self.participant_name}.log",
                    mode="w",
                ),  # Writes to file
                logging.StreamHandler(sys.stdout),  # Writes to terminal
            ],
        )

        # Create the logger instance
        self.logger = logging.getLogger(__name__)

    def get_devices(self):
        """Return list of connected ADB serials"""
        devices = self.client.devices()
        return [d.serial for d in devices]

    def connect(self, serial):
        try:
            self.d = u2.connect(serial)
            self.serial = serial
            self.logger.info(f"[{serial}] Connected")
            return True
        except Exception as e:
            self.logger.error(f"[{serial}] Failed to connect: {e}")
            return False

    def open_chrome_incognito(self, d):
        self.logger.info(f"[{d.serial}] open_chrome_incognito: START")
        self.close_meeting(d)
        time.sleep(10)

        # Launch Chrome directly in incognito with Teams URL
        d.app_start("com.android.chrome")

        # Build selector, then wait for it
        btn = d(resourceId="com.android.chrome:id/menu_button")

        if btn.wait(timeout=10):  # <-- actively waits up to 5s
            btn.click()
        else:
            raise RuntimeError("Menu button not found")

        # Click "New Incognito tab"
        incog_row = d(resourceId="com.android.chrome:id/new_incognito_tab_menu_id")
        if incog_row.wait(timeout=10):
            incog_row.click()
        else:
            raise RuntimeError("Incognito row not found")

        count = 0
        while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(f"Waiting for URL bar to appear for device {d.serial}...")
            count += 1
            if count > 60:
                raise RuntimeError("URL bar not found in time in open_chrome_incognito")

        url_bar = d(resourceId="com.android.chrome:id/url_bar")
        if url_bar.wait(timeout=10):
            url_bar.click()
            url_bar.set_text("https://www.google.com")
            d.press("enter")
        else:
            raise RuntimeError("URL bar not found in open_chrome_incognito")

        time.sleep(10)
        self.logger.info(f"[{d.serial}] open_chrome_incognito: PASS")

    def get_credentials(self):
        try:
            response = requests.get(f"{self.base_url}/get_credentials", timeout=5)
            if response.status_code == 200:
                data = response.json()
                email = data["email"].strip()
                passwd = data["password"].strip()
            else:
                self.logger.error(
                    f"Failed to get credentials: {response.json().get('log')}"
                )
                email = None
                passwd = None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during credential request: {e}")
            email = None
            passwd = None

        return email, passwd

    def login_teams(self, d, email, passwd):
        try:
            self.logger.info(f"[{d.serial}] login_teams: START")
            # Wait for the URL bar and type the Teams URL
            count = 0
            while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
                time.sleep(1)
                self.logger.info(
                    f"Waiting for URL bar to appear for device {d.serial}..."
                )
                count += 1
                if count > 60:
                    raise RuntimeError("URL bar not found in time in login_teams")
            url_bar = d(resourceId="com.android.chrome:id/url_bar")
            if url_bar.wait(timeout=10):
                url_bar.click()
                url_bar.set_text("https://teams.microsoft.com/v2")
                d.press("enter")
            else:
                raise RuntimeError("URL bar not found in login_teams")

            if not email or not passwd:
                raise RuntimeError("Email or password is None")
            count = 0
            while 'resource-id="i0116"' not in d.dump_hierarchy():
                self.logger.info(
                    f"Waiting for email input field to appear... for device {d.serial}"
                )
                time.sleep(2)
                count += 1
                if count > 60:
                    raise RuntimeError("Email input field not found in time")

            email_input = d.xpath('//*[@resource-id="i0116"]')
            if email_input.wait(timeout=30):
                email_input.set_text(email)
                d.press("enter")
            else:
                self.logger.error(f"Email input not found for device {d.serial}")
                raise RuntimeError("Email input not found")

            time.sleep(10)
            d.send_keys(passwd)

            d.press("enter")
            time.sleep(5)
            d.press("enter")
            time.sleep(20)
            self.logger.info(f"[{d.serial}] login_teams: PASS")
        except Exception as e:
            self.logger.exception(f"[{d.serial}] login_teams: FAILED | {e}")
            d.app_stop("com.android.chrome")
            raise

    def enter_meeting(self, d):
        try:
            self.logger.info(f"[{d.serial}] enter_meeting: START")
            count = 0
            while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
                time.sleep(1)
                self.logger.info(
                    f"Waiting for URL bar to appear for device {d.serial}..."
                )
                count += 1
                if count > 60:
                    raise RuntimeError("URL bar not found in time in enter_meeting")

            url_bar = d(resourceId="com.android.chrome:id/url_bar")
            if url_bar.wait(timeout=10):
                url_bar.click()
                url_bar.set_text(
                    self.meet_link,
                )
                d.press("enter")
            else:
                raise RuntimeError("URL bar not found in enter_meeting")

            d.dump_hierarchy()
            time.sleep(10)

            # Wait for the "Allow while visiting the site" button to appear
            count = 0
            while "Allow while visiting the site" not in d.dump_hierarchy():
                self.logger.info(
                    f"⏳ Waiting for 'Allow while visiting the site' button to appear... for device {d.serial}"
                )
                time.sleep(2)
                count += 1
                if count > 120:
                    raise RuntimeError(
                        "'Allow while visiting the site' not found in time"
                    )

            allow_btn = d(text="Allow while visiting the site")

            if allow_btn.wait(timeout=10):
                self.logger.info(
                    f"✅ 'Allow while visiting the site' button is present for device {d.serial}"
                )
                info = allow_btn.info

                if info.get("enabled") and info.get("clickable"):
                    allow_btn.click()
                    self.logger.info(
                        f"👉 Clicked 'Allow while visiting the site' button successfully for device {d.serial}"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ Button found but not clickable yet for device {d.serial}"
                    )

            else:
                raise RuntimeError("'Allow while visiting the site' button not found")

            d.dump_hierarchy()
            time.sleep(5)

            count = 0
            while "Turn camera on (Ctrl+Shift+O)" not in d.dump_hierarchy():
                self.logger.info(
                    f"⏳ Waiting for camera toggle button to appear... for device {d.serial}"
                )
                time.sleep(2)
                count += 1
                if count > 60:
                    raise RuntimeError("Camera toggle button not found in time")

            camera_toggle_btn = d(text="Turn camera on (Ctrl+Shift+O)")
            if camera_toggle_btn.wait(timeout=120):
                camera_toggle_btn.click()
            else:
                raise RuntimeError("Camera toggle button not found")

            join_btn = d(resourceId="prejoin-join-button")
            if join_btn.wait(timeout=60):
                join_btn.click()
            else:
                raise RuntimeError("Join button not found")
            time.sleep(10)
            self.logger.info(f"[{d.serial}] enter_meeting: PASS")
        except Exception as e:
            self.logger.exception(f"[{d.serial}] enter_meeting: FAILED | {e}")
            d.app_stop("com.android.chrome")
            raise

    def update_participation(self):

        endpoint_url = f"{self.base_url}/set_participants_joined"
        try:
            response = requests.get(endpoint_url, timeout=5)
            if response.status_code == 200:
                self.logger.info("Device participation status updated successfully.")
            else:
                self.logger.error(
                    f"Failed to update device participation status. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")

    def enable_stats(self, d):
        self.logger.info(f"[{d.serial}] enable_stats: START")
        self.update_participation()
        time.sleep(10)
        count = 0
        while "callingButtons-showMoreBtn" not in d.dump_hierarchy():
            self.logger.info(
                f"[{d.serial}] Waiting for More button to appear in call controls..."
            )
            time.sleep(1)
            count += 1
            if count > 180:
                raise RuntimeError(
                    "More button did not appear in call controls within 180 seconds"
                )
        more_btn = d(resourceId="callingButtons-showMoreBtn")
        if more_btn.wait(timeout=180):
            more_btn.click()
        else:
            raise RuntimeError("More button not found after UI indicated presence")
        settings_btn = d(resourceId="SettingsMenuControl-id")
        if settings_btn.wait(timeout=60):
            settings_btn.click()
        else:
            raise RuntimeError("Settings button not found")
        call_health_btn = d(resourceId="call-health-button")
        if call_health_btn.wait(timeout=60):
            call_health_btn.click()
        else:
            raise RuntimeError("Call health button not found")

        count = 0
        while self.start_time is None or self.end_time is None:
            self.get_start_and_end_time()
            count += 1
            if count > 60:
                self.logger.error(
                    "Failed to receive start_time and end_time within 2 minutes. Exiting script."
                )
                sys.exit(1)
            time.sleep(2)

        try:
            start_dt = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            if start_dt.tzinfo is None:
                start_dt = self.tz.localize(start_dt)
            if end_dt.tzinfo is None:
                end_dt = self.tz.localize(end_dt)
        except Exception as e:
            self.logger.error(
                f"Invalid start_time or end_time format: start_time={self.start_time}, end_time={self.end_time}, error={e}"
            )
            sys.exit(1)

        while start_dt > datetime.now(self.tz):
            time.sleep(2)
            self.logger.info("waiting for the start time")

        while end_dt > datetime.now(self.tz):
            audio_stats = {}
            video_stats = {}
            try:
                if self.audio:
                    audio_stats = self.collect_audio_stats(d)
                if self.video:
                    video_stats = self.collect_video_stats(d)
                self.send_stats_to_server(d.serial, audio_stats, video_stats)
            except Exception as e:
                self.logger.error(f"[{d.serial}] Error collecting/uploading stats: {e}")
            self.check_stop_signal()
            if self.stop_signal:
                self.logger.info("Stop signal received, exiting stats collection loop.")
                break

        self.close_meeting(d)
        self.logger.info(f"[{d.serial}] enable_stats: PASS")

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"{self.base_url}/check_stop"

            response = requests.get(
                endpoint_url, timeout=5
            )  # Replace with your Flask server URL
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    self.logger.info(
                        "Stop signal received from the server. Exiting the loop."
                    )
                else:

                    self.logger.info(
                        "No stop signal received from the server. Continuing."
                    )
            return self.stop_signal
        except Exception as e:
            self.logger.error(f"Error checking stop signal: {e}")
            return False

    def get_start_and_end_time(self):
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                self.logger.error(
                    f"Failed to fetch start/end time. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
        return None

    def close_meeting(self, d):
        d.app_stop("com.android.chrome")
        self.logger.info(f"Closed Chrome on device {d.serial}")

    def open_interop_app(self, d):
        d.app_start("com.candela.wecan")
        count = 0
        while "com.candela.wecan:id/enter_button" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(f"Waiting for Interop app to load on device {d.serial}...")
            count += 1
            if count > 60:
                raise RuntimeError(
                    f"Interop app did not load in time for device {d.serial}"
                )
        enter_test_room = d(resourceId="com.candela.wecan:id/enter_button")
        if enter_test_room.wait(timeout=10):
            enter_test_room.click()
        else:
            raise RuntimeError(
                f"Enter button not found in Interop app for device {d.serial}"
            )
        self.logger.info(f"Opened Interop app on device {d.serial}")

    def collect_audio_stats(self, d):
        self.logger.info(f"[{d.serial}] collect_audio_stats: START")
        # Wait until "View more audio data" button appears
        count = 0
        while "View more audio data" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(
                f"[{d.serial}] Waiting for 'View more audio data' button..."
            )
            count += 1
            if count > 60:
                raise RuntimeError(
                    f"Timeout waiting for 'View more audio data' button on {d.serial}"
                )

        # Open panel
        if d(text="View more audio data").wait(timeout=10):
            try:
                d(text="View more audio data").click()
                self.logger.info(f"[{d.serial}] Clicked 'View more audio data' button")
            except Exception as e:
                self.logger.warning(
                    f"[{d.serial}] Retrying click due to stale element: {e}"
                )
                time.sleep(5)
                d(text="View more audio data").click()
        else:
            raise RuntimeError(
                f"Audio panel not found or clickable for device {d.serial}"
            )

        # Wait for all resource-ids 0–7 to appear
        expected_ids = [str(i) for i in range(8)]
        count = 0

        while True:
            xml = d.dump_hierarchy()
            tree = ET.fromstring(xml)
            present_ids = {
                node.attrib.get("resource-id")
                for node in tree.findall(".//node")
                if node.attrib.get("resource-id")
            }

            missing = set(expected_ids) - present_ids
            if not missing:
                self.logger.info(f"[{d.serial}] ✅ All Audio resource-ids found")
                break

            count += 1
            if count > 30:
                raise RuntimeError(
                    f"Timeout waiting for Audio resource-ids {missing} on {d.serial}"
                )

            time.sleep(1)

        # Now safe to grab
        def grab(resource_id, default="NA", strip=""):
            try:
                parent = tree.find(f'.//*[@resource-id="{resource_id}"]')
                if parent is not None:
                    node = parent.find('node[@index="2"]')
                    if node is not None:
                        val = node.attrib.get("text", "")
                        if val:
                            return val.replace(strip, "").strip()
            except Exception as e:
                self.logger.error(
                    f"[{d.serial}] XML parse failed for {resource_id}: {e}"
                )
            return default

        audio_stats_data = {
            "au_sent_bitrate": grab("0", "0", "Kbps"),
            "au_sent_pkts": grab("1", "0", "packets"),
            "au_rtt": grab("2", "0", "ms"),
            "au_sent_codec": grab("3", "NA"),
            "au_recv_jitter": grab("4", "0", "ms"),
            "au_recv_pkt_loss": grab("5", "0", "%"),
            "au_recv_pkts": grab("6", "0", "packets"),
            "au_recv_codec": grab("7", "NA"),
        }

        count = 0
        while True:
            xml = d.dump_hierarchy()
            if "Go back to call health root panel" in xml:
                break
            time.sleep(1)
            self.logger.info(
                f"[{d.serial}] Waiting for go back to call health panel..."
            )
            count += 1
            if count > 60:
                raise RuntimeError(
                    f"Timeout waiting for 'Go back to call health root panel' on {d.serial}"
                )

        if d(text="Go back to call health root panel").wait(timeout=10):
            try:
                d(text="Go back to call health root panel").click()
                self.logger.info(
                    f"[{d.serial}] Clicked 'Go back to call health root panel'"
                )
            except Exception as e:
                self.logger.warning(
                    f"[{d.serial}] Retrying click due to stale element: {e}"
                )
                time.sleep(5)
                d(text="Go back to call health root panel").click()
        else:
            raise RuntimeError(
                f"'Go back to call health root panel' button not clickable on {d.serial}"
            )

        self.logger.info(f"[{d.serial}] collect_audio_stats: PASS")
        return audio_stats_data

    def collect_video_stats(self, d):
        self.logger.info(f"[{d.serial}] collect_video_stats: START")
        # Wait until "View more video data" button appears
        count = 0
        while "View more video data" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(
                f"[{d.serial}] Waiting for 'View more video data' button..."
            )
            count += 1
            if count > 60:
                raise RuntimeError(
                    f"Timeout waiting for 'View more video data' button on {d.serial}"
                )

        if d(text="View more video data").wait(timeout=10):
            try:
                d(text="View more video data").click()
                self.logger.info(f"[{d.serial}] Clicked 'View more video data' button")
            except Exception as e:
                self.logger.warning(
                    f"[{d.serial}] Retrying click due to stale element: {e}"
                )
                time.sleep(5)
                d(text="View more video data").click()
        else:
            raise RuntimeError(
                f"'View more video data' panel not found or clickable for device {d.serial}"
            )

        # Wait for all 8 resource-ids (0–7) to appear
        expected_ids = [str(i) for i in range(8)]
        count = 0

        while True:
            xml = d.dump_hierarchy()
            tree = ET.fromstring(xml)

            present_ids = {
                node.attrib.get("resource-id")
                for node in tree.findall(".//node")
                if node.attrib.get("resource-id")
            }

            missing = set(expected_ids) - present_ids
            if not missing:
                self.logger.info(f"[{d.serial}] ✅ All video resource-ids found")
                break

            count += 1
            if count > 30:
                raise RuntimeError(
                    f"Timeout waiting for video resource-ids {missing} on {d.serial}"
                )

            time.sleep(1)

        # Grab helper
        def grab(resource_id, default="NA", strip=""):
            try:
                parent = tree.find(f'.//*[@resource-id="{resource_id}"]')
                if parent is not None:
                    node = parent.find('node[@index="2"]')
                    if node is not None:
                        val = node.attrib.get("text", "")
                        if val:
                            return val.replace(strip, "").strip()
            except Exception as e:
                self.logger.error(
                    f"[{d.serial}] XML parse failed for {resource_id}: {e}"
                )
            return default

        # Collect video stats
        video_stats_data = {
            "vi_sent_bitrate": grab("0", "0", "Mbps"),
            "vi_recv_bitrate": grab("1", "0", "Mbps"),
            "vi_sent_frame_rate": grab("2", "0", "fps"),
            "vi_sent_res": grab("3", "NA", "px"),
            "vi_rtt": grab("4", "0", "ms"),
            "vi_sent_pkts": grab("5", "0", "packets"),
            "vi_sent_codec": grab("6", "NA"),
            "vi_processing": grab("7", "NA"),
        }

        count = 0
        while True:
            xml = d.dump_hierarchy()
            if "Go back to call health root panel" in xml:
                break
            time.sleep(1)
            self.logger.info(
                f"[{d.serial}] Waiting for go back to call health panel..."
            )
            count += 1
            if count > 60:
                raise RuntimeError(
                    f"Timeout waiting for 'Go back to call health root panel' on {d.serial}"
                )

        if d(text="Go back to call health root panel").wait(timeout=10):
            try:
                d(text="Go back to call health root panel").click()
                self.logger.info(
                    f"[{d.serial}] Clicked 'Go back to call health root panel'"
                )
            except Exception as e:
                self.logger.warning(
                    f"[{d.serial}] Retrying click due to stale element: {e}"
                )
                time.sleep(5)
                d(text="Go back to call health root panel").click()
        else:
            raise RuntimeError(
                f"'Go back to call health root panel' button not clickable on {d.serial}"
            )

        self.logger.info(f"[{d.serial}] collect_video_stats: PASS")
        return video_stats_data

    def send_stats_to_server(self, serial, audio_stats, video_stats):
        stats_data = {"timestamp": datetime.now().isoformat()}
        if self.audio:
            stats_data["audio_stats"] = audio_stats
        if self.video:
            stats_data["video_stats"] = video_stats
        payload = {self.participant_name: stats_data}

        try:
            response = requests.post(
                f"{self.base_url}/upload_stats", json=payload, timeout=5
            )
            if response.status_code == 200:
                self.logger.info(f"Stats uploaded for {self.participant_name}")
            else:
                self.logger.warning(
                    f"Failed to upload stats for {self.participant_name}: {response.status_code} - {response.text}"
                )
        except Exception as e:
            self.logger.error(
                f"Exception during upload for {self.participant_name}: {e}"
            )

    def dump_xml(self, d):
        xml = d.dump_hierarchy()
        with open(f"dump_{d.serial}.xml", "w", encoding="utf-8") as f:
            f.write(xml)


if __name__ == "__main__":

    teams_android = None

    try:

        parser = argparse.ArgumentParser(description="Teams Android Automation")
        parser.add_argument(
            "--devices",
            type=str,
            default="",
            help="Comma-separated list of device serials to use. If empty, all connected devices are used.",
        )
        parser.add_argument(
            "--meet_link",
            type=str,
            help="Teams meeting link to join.",
            required=True,
        )
        parser.add_argument(
            "--upstream_port",
            type=str,
            default=None,
            help="Upstream port for LANforge connection.",
            required=True,
        )
        parser.add_argument(
            "--audio",
            action="store_true",
            help="Enable audio stats collection.",
        )
        parser.add_argument(
            "--video",
            action="store_true",
            help="Enable video stats collection.",
        )
        parser.add_argument(
            "--participant_name",
            type=str,
            default="Test Participant",
            help="Name to use for the meeting participant.",
            required=True,
        )
        args = parser.parse_args()

        teams_android = TeamsAndroid(
            upstream_port=args.upstream_port,
            meet_link=args.meet_link,
            participant_name=args.participant_name,
        )
        teams_android.audio = args.audio
        teams_android.video = args.video
        if not teams_android.audio and not teams_android.video:
            teams_android.logger.error(
                "At least one of --audio or --video must be enabled."
            )
            sys.exit(1)

        if args.devices:
            # Although the arg might say comma-separated, we only use the first one
            serial = args.devices.split(",")[0]
            teams_android.logger.info(f"Using specified device: {serial}")
        else:
            devices = teams_android.get_devices()
            if not devices:
                teams_android.logger.error("No devices connected, exiting.")
                sys.exit(1)
            serial = devices[0]
            teams_android.logger.info(
                f"No specific device provided, using first connected device: {serial}"
            )

        if not teams_android.connect(serial):
            teams_android.logger.error("Failed to connect to device, exiting.")
            sys.exit(1)

        teams_android.logger.info(f"[{teams_android.serial}] Starting automation flow")

        try:
            teams_android.open_chrome_incognito(teams_android.d)
            email, passwd = teams_android.get_credentials()
            teams_android.login_teams(teams_android.d, email, passwd)
            teams_android.enter_meeting(teams_android.d)
            teams_android.enable_stats(teams_android.d)
            teams_android.logger.info(
                f"[{teams_android.serial}] Automation flow completed"
            )
        except RuntimeError as rt_err:
            teams_android.logger.error(
                f"[{teams_android.serial}] Flow aborted: {rt_err}"
            )
            sys.exit(1)

    except Exception as e:
        if teams_android is not None:
            teams_android.logger.error(f"Exception in main: {e}")
        else:
            logging.error(f"Exception in main before TeamsAndroid init: {e}")
        sys.exit(1)

    finally:
        if teams_android is not None and teams_android.d is not None:
            try:
                teams_android.close_meeting(teams_android.d)
            except Exception as e:
                teams_android.logger.error(
                    f"Error closing meeting for {teams_android.serial}: {e}"
                )

            try:
                teams_android.open_interop_app(teams_android.d)
                teams_android.logger.info(
                    f"open_interop_app completed for {teams_android.serial}"
                )
            except Exception as e:
                teams_android.logger.error(
                    f"Error running open_interop_app for {teams_android.serial}: {e}"
                )
