import uiautomator2 as u2
import time
from ppadb.client import Client as AdbClient
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
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
        self.devices = {}
        self.adb_serials = {}
        self.u2_sessions = {}
        self.stats = {}
        self.upstream_port = upstream_port
        self.test_serials = []
        self.stop_signal = False
        self.total_serials = []
        self.audio = True
        self.video = True
        self.meet_link = meet_link
        self.email = None
        self.passwd = None
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

    def connect_one_device(self, serial, timeout=20):
        ex = ThreadPoolExecutor(max_workers=1)
        fut = ex.submit(u2.connect, serial)
        try:
            d = fut.result(timeout=timeout)
            self.logger.info(f"[{serial}] Connected")
            return serial, d
        except TimeoutError:
            self.logger.error(f"[{serial}] ⏳ Connection timeout")
            fut.cancel()  # best-effort; won't stop a running thread
            # IMPORTANT: don't wait for the stuck worker
            ex.shutdown(wait=False, cancel_futures=True)
            return None, None
        except Exception as e:
            self.logger.error(f"[{serial}] Failed to connect: {e}")
            ex.shutdown(wait=False, cancel_futures=True)
            return None, None
        else:
            ex.shutdown(wait=True)

    def connect_multiple_devices(self):
        sessions = {}
        with ThreadPoolExecutor(max_workers=len(self.total_serials)) as ex:
            futures = {
                ex.submit(self.connect_one_device, serial): serial
                for serial in self.total_serials
            }
            for future in as_completed(futures):
                serial, d = future.result()
                if serial and d:
                    sessions[serial] = d
        self.u2_sessions = sessions
        self.test_serials = list(sessions.keys())

    def run_on_multiple_devices(self, device_serials, max_workers=5):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.open_chrome_incognito, serial)
                for serial in device_serials
            ]
            # Wait for all to complete
            for future in futures:
                future.result()

    def open_chrome_incognito(self, serial):
        d = self.u2_sessions[serial]
        self.close_meeting(d)
        time.sleep(10)

        # Launch Chrome directly in incognito with Teams URL
        d.app_start("com.android.chrome")

        # Build selector, then wait for it
        btn = d(resourceId="com.android.chrome:id/menu_button")

        if btn.wait(timeout=10):  # <-- actively waits up to 5s
            btn.click()
        else:
            raise Exception(f"Menu button not found for device {d.serial}")

        # Click "New Incognito tab"
        incog_row = d(resourceId="com.android.chrome:id/new_incognito_tab_menu_id")
        if incog_row.wait(timeout=10):
            incog_row.click()
        else:
            raise Exception(f"Incognito row not found for device {d.serial}")

        count = 0
        while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(f"Waiting for URL bar to appear for device {d.serial}...")
            count += 1
            if count > 60:
                raise Exception(
                    f"URL bar not found in time for device {d.serial} in open_chrome_incognito method"
                )

        url_bar = d(resourceId="com.android.chrome:id/url_bar")
        if url_bar.wait(timeout=10):
            url_bar.click()
            url_bar.set_text("https://www.google.com")
            d.press("enter")
        else:
            raise Exception(
                f"URL bar not found for device {d.serial} in open_chrome_incognito method"
            )

        time.sleep(10)

        btn = d(resourceId="com.android.chrome:id/menu_button")

        if btn.wait(timeout=10):  # <-- actively waits up to 5s
            btn.click()
        else:
            raise Exception(f"Menu button not found for device {d.serial}")

        node = d(resourceId="com.android.chrome:id/menu_item_text", text="Desktop site")
        if node.wait(timeout=10):
            info = node.info
            checked = info.get("checked")

            if checked is True:
                self.logger.info(
                    f"Desktop site is already ENABLED for device {d.serial}"
                )
            elif checked is False:
                self.logger.info(
                    f"Desktop site is DISABLED — enabling now... for device {d.serial}"
                )
                node.click()
                time.sleep(2)
                self.logger.info(
                    f"Desktop site ENABLED successfully for device {d.serial}"
                )
            else:
                self.logger.warning(
                    f"Could not determine checked state for Desktop site for device {d.serial}"
                )
        else:
            raise Exception(f"Desktop site menu item not found for device {d.serial}")

        email, passwd = self.get_credentials()

        self.login_teams(d, email, passwd)

    def get_credentials(self):
        try:
            response = requests.get(
                f"http://{self.upstream_port}:5005/get_credentials", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                email = data["email"].strip()
                passwd = data["password"].strip()
            else:
                logging.error(
                    f"Failed to get credentials: {response.json().get('log')}"
                )
                email = None
                passwd = None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during credential request: {e}")
            email = None
            passwd = None

        return email, passwd

    def login_teams(self, d, email, passwd):
        try:
            # Wait for the URL bar and type the Teams URL
            count = 0
            while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
                time.sleep(1)
                self.logger.info(
                    f"Waiting for URL bar to appear for device {d.serial}..."
                )
                count += 1
                if count > 60:
                    raise Exception(
                        f"URL bar not found in time for device {d.serial} in login teams method"
                    )
            url_bar = d(resourceId="com.android.chrome:id/url_bar")
            if url_bar.wait(timeout=10):
                url_bar.click()
                url_bar.set_text("https://teams.microsoft.com/v2")
                d.press("enter")
            else:
                raise Exception(f"URL bar not found for device {d.serial}")

            if not email or not passwd:
                raise Exception(f"Email or password is None for device {d.serial}")
            count = 0
            while 'resource-id="i0116"' not in d.dump_hierarchy():
                self.logger.info(
                    f"Waiting for email input field to appear... for device {d.serial}"
                )
                time.sleep(2)
                count += 1
                if count > 60:
                    raise Exception(
                        f"Email input field not found in time for device {d.serial}"
                    )

            email_input = d.xpath('//*[@resource-id="i0116"]')
            if email_input.wait(timeout=30):
                email_input.set_text(email)
                d.press("enter")
            else:
                self.logger.error(f"Email input not found for device {d.serial}")
                raise Exception(f"Email input not found for device {d.serial}")

            time.sleep(10)
            d.send_keys(passwd)

            d.press("enter")
            time.sleep(5)
            d.press("enter")
            time.sleep(20)
            self.enter_meeting(d)
        except Exception as e:
            self.logger.error(f"❌ Exception during login for device {d.serial}: {e}")
            d.app_stop("com.android.chrome")

    def enter_meeting(self, d):
        try:
            count = 0
            while "com.android.chrome:id/url_bar" not in d.dump_hierarchy():
                time.sleep(1)
                self.logger.info(
                    f"Waiting for URL bar to appear for device {d.serial}..."
                )
                count += 1
                if count > 60:
                    raise Exception(
                        f"❌ URL bar not found in time for device {d.serial} in enter_meeting method"
                    )

            url_bar = d(resourceId="com.android.chrome:id/url_bar")
            if url_bar.wait(timeout=10):
                url_bar.click()
                url_bar.set_text(
                    self.meet_link,
                )
                d.press("enter")
            else:
                raise Exception(
                    f"URL bar not found for device {d.serial} in enter_meeting method"
                )

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
                    raise Exception(
                        f"❌ 'Allow while visiting the site' button not found in time for device {d.serial}"
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
                raise Exception(
                    f"❌ 'Allow while visiting the site' button not found for device {d.serial}"
                )

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
                    raise Exception(
                        f"Camera toggle button not found in time for device {d.serial}"
                    )
            
            camera_toggle_btn = d(text="Turn camera on (Ctrl+Shift+O)")
            if camera_toggle_btn.wait(timeout=60):
                camera_toggle_btn.click()
            else:
                raise Exception(
                    f"Camera toggle button not found for device {d.serial}"
                )

            join_btn = d(resourceId="prejoin-join-button")
            if join_btn.wait(timeout=60):
                join_btn.click()
            else:
                raise Exception(f"Join button not found for device {d.serial}")
            time.sleep(10)
            self.enable_stats(d)
        except Exception as e:
            self.logger.error(
                f"❌ Exception during meeting entry for device {d.serial}: {e}"
            )
            d.app_stop("com.android.chrome")

    def update_participation(self):

        endpoint_url = f"{self.base_url}/set_participants_joined"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                self.logger.info("Device participation status updated successfully.")
            else:
                self.logger.error(
                    f"Failed to update device participation status. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")

    def enable_stats(self, d):
        self.update_participation()
        time.sleep(10)
        xml = d.dump_hierarchy()
        while "callingButtons-showMoreBtn" not in xml:
            time.sleep(1)
            xml = d.dump_hierarchy()
            self.logger.info("Waiting for More button to appear in call controls...")
        more_btn = d(resourceId="callingButtons-showMoreBtn")
        if more_btn.wait(timeout=180):
            more_btn.click()
        else:
            self.logger.error("More button not found")
            return
        settings_btn = d(resourceId="SettingsMenuControl-id")
        if settings_btn.wait(timeout=60):
            settings_btn.click()
        else:
            self.logger.error("Settings button not found")
            return
        call_health_btn = d(resourceId="call-health-button")
        if call_health_btn.wait(timeout=60):
            call_health_btn.click()
        else:
            self.logger.error("Call health button not found")
            return

        while self.start_time is None or self.end_time is None:
            self.get_start_and_end_time()
            time.sleep(2)

        while self.start_time > datetime.now(self.tz).isoformat():
            time.sleep(2)
            self.logger.info("waiting for the start time")

        while self.end_time > datetime.now(self.tz).isoformat():
            if self.audio:
                audio_stats = self.collect_audio_stats(d)
            if self.video:
                video_stats = self.collect_video_stats(d)
            self.send_stats_to_server(d.serial, audio_stats, video_stats)

        self.close_meeting(d)

    def get_start_and_end_time(self):
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                self.logger.error(
                    f"Failed to fetch new login URL. Status code: {response.status_code}"
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
                raise Exception(
                    f"Interop app did not load in time for device {d.serial}"
                )
        enter_test_room = d(resourceId="com.candela.wecan:id/enter_button")
        if enter_test_room.wait(timeout=10):
            enter_test_room.click()
        else:
            raise Exception(
                f"Enter button not found in Interop app for device {d.serial}"
            )
        self.logger.info(f"Opened Interop app on device {d.serial}")

    def collect_audio_stats(self, d):
        # Wait until "View more audio data" button appears
        while "View more audio data" not in d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(
                f"Waiting for View more audio data button to appear for {d.serial}..."
            )

        # Open panel
        if d(text="View more audio data").wait(timeout=10):
            try:
                d(text="View more audio data").click()
            except Exception as e:
                self.logger.warning(f"Retrying click due to stale element: {e}")
                time.sleep(5)
                d(text="View more audio data").click()
        else:
            self.logger.warning(
                f"Audio panel not found for device {d.serial}, skipping..."
            )
            return

        # Wait for all resource-ids 0–7 to appear
        expected_ids = [str(i) for i in range(8)]
        timeout = 30
        start = time.time()

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
                self.logger.info(f"✅ All Audio resource-ids found for {d.serial}")
                break

            if time.time() - start > timeout:
                self.logger.warning(
                    f"⚠️ Timeout waiting for Audio resource-ids {missing} on {d.serial}"
                )
                break

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
                self.logger.error(f"XML parse failed for {resource_id}: {e}")
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

        while True:
            xml = d.dump_hierarchy()
            if "Go back to call health root panel" in xml:
                break
            time.sleep(1)
            self.logger.info(f"Waiting for go back to call health panel for {d.serial}")

        if d(text="Go back to call health root panel").wait(timeout=10):
            try:
                d(text="Go back to call health root panel").click()
            except Exception as e:
                self.logger.warning(f"Retrying click due to stale element: {e}")
                time.sleep(5)
                d(text="Go back to call health root panel").click()

        return audio_stats_data

    def collect_video_stats(self, d):
        # Wait until "View more video data" button appears
        xml = d.dump_hierarchy()
        while "View more video data" not in xml:
            time.sleep(1)
            xml = d.dump_hierarchy()
            self.logger.info(
                f"Waiting for View more video data button to appear for {d.serial}..."
            )

        if d(text="View more video data").wait(timeout=10):
            try:
                d(text="View more video data").click()
            except Exception as e:
                self.logger.warning(f"Retrying click due to stale element: {e}")
                time.sleep(5)
                d(text="View more video data").click()
        else:
            self.logger.warning(
                f"Video panel not found for device {d.serial}, skipping..."
            )
            return

        # Wait for all 8 resource-ids (0–7) to appear
        expected_ids = [str(i) for i in range(8)]
        timeout = 30
        start = time.time()

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
                self.logger.info(f"✅ All video resource-ids found for {d.serial}")
                break

            if time.time() - start > timeout:
                self.logger.warning(
                    f"Timeout waiting for video resource-ids {missing} on {d.serial}"
                )
                break

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
                self.logger.error(f"XML parse failed for {resource_id}: {e}")
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

        while True:
            xml = d.dump_hierarchy()
            if "Go back to call health root panel" in xml:
                break
            time.sleep(1)
            self.logger.info(f"Waiting for go back to call health panel for {d.serial}")

        if d(text="Go back to call health root panel").wait(timeout=10):
            try:
                d(text="Go back to call health root panel").click()
            except Exception as e:
                self.logger.warning(f"Retrying click due to stale element: {e}")
                time.sleep(5)
                d(text="Go back to call health root panel").click()

        return video_stats_data

    def send_stats_to_server(self, serial, audio_stats, video_stats):
        if self.audio:
            payload = {
                self.participant_name: {
                    "timestamp": datetime.now().isoformat(),
                    "audio_stats": audio_stats,
                }
            }
        if self.video:
            payload = {
                self.participant_name: {
                    "timestamp": datetime.now().isoformat(),
                    "video_stats": video_stats,
                }
            }
        if self.audio and self.video:
            payload = {
                self.participant_name: {
                    "timestamp": datetime.now().isoformat(),
                    "audio_stats": audio_stats,
                    "video_stats": video_stats,
                }
            }

        try:
            response = requests.post(f"{self.base_url}/upload_stats", json=payload)
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
            default="https://teams.microsoft.com/meet/4950863846706?p=hR18cFksPeV0cbgMbz",
            help="Teams meeting link to join.",
        )
        parser.add_argument(
            "--upstream_port",
            type=str,
            default=None,
            help="Upstream port for LANforge connection.",
        )
        parser.add_argument(
            "--audio", action="store_true", help="Enable audio stats collection."
        )
        parser.add_argument(
            "--video", action="store_true", help="Enable video stats collection."
        )
        parser.add_argument(
            "--duration",
            type=int,
            default=2,
            help="Duration in minutes to run the test on each device.",
        )
        parser.add_argument(
            "--participant_name",
            type=str,
            default="Test Participant",
            help="Name to use for the meeting participant.",
        )
        args = parser.parse_args()

        teams_android = TeamsAndroid(
            upstream_port=args.upstream_port,
            meet_link=args.meet_link,
            participant_name=args.participant_name,
        )
        if args.devices:
            specified_serials = args.devices.split(",")
            teams_android.logger.info(f"Using specified devices: {specified_serials}")
        else:
            specified_serials = None
            teams_android.logger.info(
                "No specific devices provided, using all connected devices."
            )
        teams_android.total_serials = teams_android.get_devices()
        teams_android.logger.info(f"Found devices: {teams_android.total_serials}")
        if "all" in specified_serials:
            specified_serials = None
        if specified_serials:
            teams_android.total_serials = [
                s for s in teams_android.total_serials if s in specified_serials
            ]
            teams_android.logger.info(
                f"Filtered devices to use: {teams_android.total_serials}"
            )
        teams_android.connect_multiple_devices()
        teams_android.logger.info(f"Connected devices: {teams_android.test_serials}")

        if not teams_android.test_serials:
            teams_android.logger.error("No devices connected, exiting.")
            exit(1)
        teams_android.run_on_multiple_devices(
            teams_android.test_serials,
            max_workers=len(teams_android.test_serials),
        )
    except Exception as e:
        teams_android.logger.error(f"Exception in main: {e}")
        for serial, d in teams_android.u2_sessions.items():
            teams_android.close_meeting(d)
        teams_android.logger.info("All meetings closed, exiting.")

    finally:
        with ThreadPoolExecutor(max_workers=len(teams_android.u2_sessions)) as executor:
            futures = {
                executor.submit(teams_android.open_interop_app, d): serial
                for serial, d in teams_android.u2_sessions.items()
            }

            for future in as_completed(futures):
                serial = futures[future]
                try:
                    future.result()  # wait for this thread to finish
                    teams_android.logger.info(
                        f"open_interop_app completed for {serial}"
                    )
                except Exception as e:
                    teams_android.logger.error(
                        f"Error running open_interop_app for {serial}: {e}"
                    )