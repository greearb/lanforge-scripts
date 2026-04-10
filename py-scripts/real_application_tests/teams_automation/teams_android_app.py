import uiautomator2 as u2
import time
from ppadb.client import Client as AdbClient
from datetime import datetime
import argparse
import pytz
import requests
import logging
import os
import sys
import traceback
import subprocess


class TeamsAndroidApp:
    def __init__(
        self,
        host="127.0.0.1",
        port=5037,
        upstream_port=None,
        meet_link=None,
        participant_name=None,
        serial=None,
        audio=True,
        video=True,
    ):
        self.host = host
        self.client = AdbClient(host=self.host, port=port)
        self.serial = serial
        self.d = None
        self.upstream_port = upstream_port
        self.stop_signal = False
        self.audio = audio
        self.video = video
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

    def connect(self):
        self.d = u2.connect(self.serial)
        self.logger.info(f"[{self.participant_name} ({self.serial})] Connected")

    def is_app_installed(self, package_name):
        """Check if an app is installed on the device."""
        result = subprocess.run(
            ["adb", "-s", self.serial, "shell", "pm", "list", "packages", package_name],
            capture_output=True, text=True
        )
        installed = f"package:{package_name}" in result.stdout
        if not installed:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] App '{package_name}' is not installed on the device."
            )
        return installed

    def update_participation(self):

        endpoint_url = f"{self.base_url}/set_participants_joined"
        try:
            response = requests.get(endpoint_url, timeout=5)
            if response.status_code == 200:
                self.logger.info(
                    f"[{self.participant_name} ({self.serial})] Device participation status updated successfully."
                )
            else:
                self.logger.error(
                    f"[{self.participant_name} ({self.serial})] Failed to update device participation status. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Request error: {e}"
            )

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"{self.base_url}/check_stop"

            response = requests.get(
                endpoint_url, timeout=5
            )
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
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Error checking stop signal: {e}"
            )
            return self.stop_signal

    def close_meeting(self):
        if self.d is not None:
            self.d.app_stop("com.microsoft.teams")
            self.logger.info(
                f"Closed Teams App on device {self.participant_name} ({self.serial})"
            )

    def open_interop_app(self):
        if self.d is None:
            return
        self.d.app_start("com.candela.wecan")
        count = 0
        while "com.candela.wecan:id/enter_button" not in self.d.dump_hierarchy():
            time.sleep(1)
            self.logger.info(
                f"Waiting for Interop app to load on device {self.participant_name} ({self.serial})..."
            )
            count += 1
            if count > 60:
                raise Exception(
                    f"Interop app did not load in time for device {self.participant_name} ({self.serial})"
                )
        enter_test_room = self.d(resourceId="com.candela.wecan:id/enter_button")
        if enter_test_room.wait(timeout=10):
            enter_test_room.click()
        else:
            raise Exception(
                f"Enter button not found in Interop app for device {self.participant_name} ({self.serial})"
            )
        self.logger.info(
            f"Opened Interop app on device {self.participant_name} ({self.serial})"
        )

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
                    f"[{self.participant_name} ({self.serial})] Failed to fetch Start Time and End Time of the Test. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Request error: {e}"
            )

    def dump_xml(self):
        xml = self.d.dump_hierarchy()
        with open(f"dump_{self.d.serial}.xml", "w", encoding="utf-8") as f:
            f.write(xml)

    def enable_audio(self):
        wait_count = 0
        while (
            "Mic muted" not in self.d.dump_hierarchy()
            and "Mic unmuted" not in self.d.dump_hierarchy()
        ):
            time.sleep(1)
            self.logger.info(
                f"Waiting for Mute/Unmute button to be available for device {self.participant_name} ({self.serial})..."
            )
            wait_count += 1
            if wait_count > 60:
                self.logger.error(
                    f"Mute/Unmute button not found in time for device {self.participant_name} ({self.serial})"
                )
                return
        if "Mic unmuted" in self.d.dump_hierarchy():
            self.logger.info(
                f"Audio is already unmuted for device {self.participant_name} ({self.serial})"
            )
            return
        else:
            unmute_btn = self.d(description="Mic muted")
            if unmute_btn.wait(timeout=20):
                unmute_btn.click()
                self.logger.info(
                    f"[{self.participant_name} ({self.serial})] Un Mute button clicked to unmute audio."
                )
            else:
                self.logger.error(
                    f"[{self.participant_name} ({self.serial})] Un Mute button not found to click."
                )

    def enable_video(self):
        count = 0
        while (
            "Video is off" not in self.d.dump_hierarchy()
            and "Video is on" not in self.d.dump_hierarchy()
        ):
            time.sleep(1)
            self.logger.info(
                f"Waiting for Video Turn on button {self.participant_name} ({self.serial})..."
            )
            count += 1
            if count > 60:
                self.logger.error(
                    f"Unable to find Video Turn on Button or Video Turn off Button {self.participant_name} ({self.serial})"
                )
                return
        if "Video is on" in self.d.dump_hierarchy():
            self.logger.info(
                f"Video is already on for Device {self.participant_name} - {self.serial}"
            )
            return
        else:
            video_btn = self.d(description="Video is off")
            if video_btn.wait(timeout=20):
                video_btn.click()
                self.logger.info(
                    f"[{self.participant_name} ({self.serial})] Video Turn on button clicked to enable video."
                )
            else:
                self.logger.error(
                    f"[{self.participant_name} ({self.serial})] Video Turn on button not found to click."
                )

    def join_meeting(self):
        subprocess.run(
            [
                "adb",
                "-s",
                self.serial,
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-d",
                self.meet_link,
                "com.microsoft.teams",
            ]
        )

        if self.video:
            self.enable_video()
        if self.audio:
            self.enable_audio()

        self.enter_participant_name()

        wait_count = 0
        while "Join now" not in self.d.dump_hierarchy():
            time.sleep(1)
            wait_count += 1
            self.logger.info(
                f"Waiting for meeting join screen to load on device {self.participant_name} ({self.serial})..."
            )
            if wait_count > 60:
                self.logger.error(
                    f"Meeting join screen did not load in time for device {self.participant_name} ({self.serial})"
                )
                sys.exit(1)

        join_btn = self.d.xpath('//*[@text="Join now"]')

        if join_btn.wait(timeout=20):
            join_btn.click()
            self.logger.info(
                f"[{self.participant_name} ({self.serial})] Join now button clicked."
            )
        else:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Join now button not found to click."
            )
            sys.exit(1)

    def enter_participant_name(self):
        wait_count = 0
        while "Enter name" not in self.d.dump_hierarchy():
            time.sleep(1)
            wait_count += 1
            self.logger.info(
                f"Waiting for participant name input field to be available for device {self.participant_name} ({self.serial})..."
            )
            if wait_count > 60:
                self.logger.error(
                    f"Participant name input field did not appear in time for device {self.participant_name} ({self.serial})"
                )
                sys.exit(1)
        name_input = self.d.xpath('//*[@text="Enter name"]')
        if name_input.wait(timeout=20):
            name_input.set_text(self.participant_name)
            self.logger.info(
                f"[{self.participant_name} ({self.serial})] Participant name entered."
            )
            time.sleep(2)
        else:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Participant name input field not found to enter name."
            )
            sys.exit(1)


if __name__ == "__main__":
    teams_android_app = None
    try:

        parser = argparse.ArgumentParser(description="Teams Android App Automation")
        parser.add_argument("--upstream_port", type=str, help="Upstream server port")
        parser.add_argument("--meet_link", type=str, help="Teams meeting link")
        parser.add_argument("--participant_name", type=str, help="Participant name")
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
            "--device",
            type=str,
            default="",
            help="Comma-separated list of device serials to use. If empty, all connected devices are used.",
            required=True,
        )
        args = parser.parse_args()

        teams_android_app = TeamsAndroidApp(
            upstream_port=args.upstream_port,
            meet_link=args.meet_link,
            participant_name=args.participant_name,
            serial=args.device.strip(),
            audio=args.audio,
            video=args.video,
        )

        test_device_serial = args.device.strip()

        total_devices = teams_android_app.get_devices()
        if test_device_serial not in total_devices:
            logging.error(
                f"Specified device serial '{test_device_serial}' not found among connected devices: {total_devices}"
            )
            sys.exit(1)

        teams_android_app.connect()

        if not teams_android_app.is_app_installed("com.microsoft.teams"):
            sys.exit(1)
        if not teams_android_app.is_app_installed("com.candela.wecan"):
            sys.exit(1)

        teams_android_app.join_meeting()
        teams_android_app.update_participation()
        count = 0
        while (
            teams_android_app.start_time is None
            or teams_android_app.end_time is None
        ):
            teams_android_app.get_start_and_end_time()
            count += 1
            if count > 60:
                teams_android_app.logger.error(
                    "Failed to receive start_time and end_time within 2 minutes. Exiting script."
                )
                sys.exit(1)
            time.sleep(2)

        try:
            start_dt = datetime.fromisoformat(
                teams_android_app.start_time.replace("Z", "+00:00")
            )
            end_dt = datetime.fromisoformat(
                teams_android_app.end_time.replace("Z", "+00:00")
            )
            if start_dt.tzinfo is None:
                start_dt = teams_android_app.tz.localize(start_dt)
            if end_dt.tzinfo is None:
                end_dt = teams_android_app.tz.localize(end_dt)
        except Exception as e:
            teams_android_app.logger.error(
                f"Invalid start_time or end_time format: start_time={teams_android_app.start_time}, end_time={teams_android_app.end_time}, error={e}"
            )
            sys.exit(1)

        while start_dt > datetime.now(teams_android_app.tz):
            time.sleep(2)
            teams_android_app.logger.info("waiting for the start time")

        while end_dt > datetime.now(teams_android_app.tz):
            teams_android_app.check_stop_signal()
            time.sleep(5)
            if teams_android_app.stop_signal:
                teams_android_app.logger.info(
                    "Stop signal received, exiting stats collection loop."
                )
                break
        # teams_android_app.dump_xml()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        if teams_android_app:
            teams_android_app.close_meeting()
            try:
                teams_android_app.open_interop_app()
            except Exception as e:
                logging.error(f"Failed to open interop app: {e}")
