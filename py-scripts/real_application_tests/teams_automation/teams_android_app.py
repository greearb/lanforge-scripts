import argparse
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime

import pytz
import requests
import uiautomator2 as u2
from ppadb.client import Client as AdbClient


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
        prejoin_timeout=180,
    ):
        self.prejoin_timeout = prejoin_timeout
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

        # Store mobile logs in a fixed location relative to this script, independent of the current working directory.
        mobile_log_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ms_teams_mobile_logs",
        )
        os.makedirs(mobile_log_dir, exist_ok=True)

        log_name = (
            f"{self.participant_name}_{self.serial}.log"
            if self.serial
            else f"{self.participant_name}.log"
        )

        # Configure the logging system
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    os.path.join(mobile_log_dir, log_name),
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

    def _adb(self, *args):
        """Run an adb shell command on this device and return the result."""
        return subprocess.run(
            ["adb", "-s", self.serial, "shell", *args],
            capture_output=True,
            text=True,
        )

    def grant_permissions(self, package_name="com.microsoft.teams"):
        """Pre-grant the app's runtime permissions so no dialog blocks the join.

        Reads the permissions the package actually declares on this device, so
        one call covers every API level in the fleet. Returns the number still
        ungranted afterwards.
        """
        listing = self._adb("dumpsys", "package", package_name).stdout
        wanted, in_runtime = [], False
        for raw in listing.splitlines():
            line = raw.strip()
            if line.startswith("runtime permissions:"):
                in_runtime = True
            elif in_runtime:
                if line.startswith("android.permission."):
                    wanted.append(line.split(":", 1)[0])
                elif line:
                    break

        granted = 0
        for permission in wanted:
            result = self._adb("pm", "grant", package_name, permission)
            output = result.stdout + result.stderr
            if "GRANT_RUNTIME_PERMISSIONS" in output:
                self.logger.error(
                    f"[{self.participant_name} ({self.serial})] This ROM blocks adb from "
                    f"granting permissions. Accept the prompts manually once."
                )
                break
            if not output.strip():
                granted += 1

        # Not a runtime permission — it is an appop, so pm grant cannot set it.
        self._adb("appops", "set", package_name, "SYSTEM_ALERT_WINDOW", "allow")

        remaining = self._adb("dumpsys", "package", package_name).stdout.count(
            "granted=false"
        )
        self.logger.info(
            f"[{self.participant_name} ({self.serial})] Permissions: granted {granted}"
            f"/{len(wanted)}, {remaining} still ungranted."
        )
        return remaining

    def update_participation(self):

        endpoint_url = f"{self.base_url}/set_participants_joined"
        try:
            # Include the participant name so the server can identify which device joined the call.
            response = requests.get(endpoint_url, params={"device": self.participant_name}, timeout=5)
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

    def _hierarchy(self):
        """One UI dump. A failed dump means 'nothing readable on screen yet'."""
        try:
            return self.d.dump_hierarchy()
        except Exception as e:
            self.logger.debug(
                f"[{self.participant_name} ({self.serial})] UI dump failed: {e}"
            )
            return ""

    def wait_for_text(self, texts, timeout, what):
        """Poll the UI until any string in texts appears. Return the hierarchy, or "".

        One dump per poll, and a wall-clock deadline rather than an iteration
        count. dump_hierarchy() takes seconds on a loading screen, so counting
        iterations turns a nominal 60s limit into several minutes — which is
        what made a slow Teams launch look like a hang.
        """
        deadline = time.monotonic() + timeout
        announced_loading = False
        while True:
            xml = self._hierarchy()
            if any(t in xml for t in texts):
                return xml

            if not announced_loading and ("Hang tight" in xml or "Loading" in xml):
                # Distinguishes "Teams is still starting" from "the screen we
                # want never appeared", which read identically in the old logs.
                self.logger.info(
                    f"[{self.participant_name} ({self.serial})] Teams is still loading; "
                    f"waiting for {what}."
                )
                announced_loading = True

            if time.monotonic() >= deadline:
                self.logger.error(
                    f"[{self.participant_name} ({self.serial})] {what} did not appear "
                    f"within {timeout}s."
                )
                return ""
            time.sleep(1)

    def enable_audio(self, timeout=60):
        xml = self.wait_for_text(
            ("Mic muted", "Mic unmuted"), timeout, "Mute/Unmute button"
        )
        if not xml:
            return
        if "Mic unmuted" in xml:
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

    def enable_video(self, timeout=60):
        xml = self.wait_for_text(
            ("Video is off", "Video is on"), timeout, "Video on/off button"
        )
        if not xml:
            return
        if "Video is on" in xml:
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

    def _launch_meeting_intent(self):
        """Hand the meeting link to Teams as a VIEW intent."""
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

    def _current_activity(self):
        """Return the foreground activity name, or "" if it cannot be read."""
        try:
            return self.d.app_current().get("activity", "")
        except Exception as e:
            self.logger.debug(
                f"[{self.participant_name} ({self.serial})] app_current failed: {e}"
            )
            return ""

    def join_meeting(self):
        attempts = 3
        per_attempt = max(30, self.prejoin_timeout // attempts)
        for attempt in range(1, attempts + 1):
            self._launch_meeting_intent()
            if self.wait_for_text(
                ("Enter name", "Join now"), per_attempt, "Teams pre-join screen"
            ):
                break
            self.logger.warning(
                f"[{self.participant_name} ({self.serial})] attempt {attempt}/{attempts}: "
                f"no pre-join screen after {per_attempt}s, still on "
                f"{self._current_activity() or 'unknown activity'}."
            )
            if attempt < attempts:
                self.d.app_stop("com.microsoft.teams")
                time.sleep(2)
        else:
            self.logger.error(
                f"[{self.participant_name} ({self.serial})] Teams did not reach the "
                f"pre-join screen after {attempts} attempts."
            )
            sys.exit(1)

        self.enter_participant_name()

        if self.video:
            self.enable_video()
        if self.audio:
            self.enable_audio()

        if not self.wait_for_text(("Join now",), 60, "Join now button"):
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

    def enter_participant_name(self, timeout=60):
        if not self.wait_for_text(("Enter name",), timeout, "participant name field"):
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

        # Before the join, so a first-launch permission dialog cannot sit on top
        # of the pre-join screen the automation is waiting for.
        teams_android_app.grant_permissions()

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
