#!/usr/bin/env python3
"""Drive a single Android device through a Zoom call for LANforge interop tests."""

import argparse
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from xml.etree.ElementTree import fromstring

import pytz
import requests
import uiautomator2 as u2
from ppadb.client import Client as AdbClient

# from ping_monitor import PingMonitor

ZOOM_PACKAGE = "us.zoom.videomeetings"


class ZoomAutomator:
    """Drive one Android device through a Zoom meeting.

    Talks to the device over ADB for shell commands and uiautomator2 for UI
    interaction, and to the host's Flask server for meeting timing and stop
    signals. One instance drives one device; the participant name keys both
    its log file and everything it uploads to the host.
    """

    def __init__(
        self,
        host="127.0.0.1",
        port=5037,
        server_ip="127.0.0.1",
        server_port=5000,
        participant_name=None,
    ):
        """Set up the ADB client and this participant's logger.

        host/port address the ADB server, server_ip/server_port the host's
        Flask server. No device is attached yet — call set_device() for that.
        """
        self.host = host
        self.port = port
        self.client = AdbClient(host=host, port=port)
        self.device_serial = None
        self.u2_device = None
        self.base_url = "http://{server_ip}:{server_port}".format(
            server_ip=server_ip, server_port=server_port
        )
        self.start_time = None
        self.end_time = None
        self.adb_device = None
        self.stop_signal = False
        self.tz = pytz.timezone("Asia/Kolkata")
        self.participant_name = participant_name or "android_zoom"
        self.logger = self._create_logger()
        # self.ping_monitor = PingMonitor(self.participant_name)

    def _create_logger(self):
        """Build this participant's logger, writing to file and to stdout.

        The file is zoom_mobile_logs/<participant>.log, which upload_log() later
        pushes to the host, and stdout is what LANforge captures for this device's
        generic endpoint.
        """
        log_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "zoom_mobile_logs"
        )
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir

        logger_name = f"{__name__}.{self.participant_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

            file_handler = logging.FileHandler(
                os.path.join(log_dir, f"{self.participant_name}.log"), mode="w"
            )
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

        return logger

    def _set_phase(self, phase):
        """Mark a new stage of the run in the log, in one place."""
        self.logger.info(f"--- {phase} ---")

    @staticmethod
    def _parse_bounds(bounds):
        """Turn a uiautomator bounds string into (left, top, right, bottom).

        Returns None if bounds is missing or does not match "[x1,y1][x2,y2]".
        """
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
        if not match:
            return None
        return tuple(map(int, match.groups()))

    def tap_bounds_center(self, d, bounds):
        """Tap the middle of a uiautomator bounds rectangle.

        Returns False without tapping if the bounds could not be parsed.
        """
        parsed = self._parse_bounds(bounds)
        if not parsed:
            return False

        left, top, right, bottom = parsed
        d.click((left + right) // 2, (top + bottom) // 2)
        return True

    def reveal_zoom_controls(self, d, tap_coords):
        """Tap the screen until Zoom's auto-hiding meeting toolbar is showing.

        Returns as soon as the audio or video button is visible, after at most
        two taps; the controls have to be on screen before they can be read.
        """
        audio_state, _, _ = self.get_audio_control_info(d)
        video_state, _, _ = self.get_video_control_info(d)
        if audio_state is not None or video_state is not None:
            return

        d.click(*tap_coords)
        time.sleep(0.8)

        audio_state, _, _ = self.get_audio_control_info(d)
        video_state, _, _ = self.get_video_control_info(d)
        if audio_state is not None or video_state is not None:
            return

        d.click(*tap_coords)
        time.sleep(1)

    def get_audio_control_info(self, d):
        """Return audio state and bounds by parsing the current hierarchy dump."""
        try:
            root = fromstring(d.dump_hierarchy())
        except Exception as e:
            self.logger.error(
                f"Failed to parse audio hierarchy: {e}"
            )
            return None, None, None

        for node in root.iter("node"):
            content_desc = node.attrib.get("content-desc", "")
            if content_desc == "Mute my audio, button":
                return True, node.attrib.get("bounds"), content_desc
            if content_desc == "Unmute my audio, button":
                return False, node.attrib.get("bounds"), content_desc

        return None, None, None

    def get_video_control_info(self, d):
        """Return Video state and bounds by parsing the current hierarchy dump."""
        try:
            root = fromstring(d.dump_hierarchy())
        except Exception as e:
            self.logger.error(
                f"Failed to parse video hierarchy: {e}"
            )
            return None, None, None

        for node in root.iter("node"):
            content_desc = node.attrib.get("content-desc", "")
            if content_desc == "Start my video, button":
                return False, node.attrib.get("bounds"), content_desc
            if content_desc == "Stop my video, button":
                return True, node.attrib.get("bounds"), content_desc

        return None, None, None

    def get_leave_control_info(self, d):
        """Return leave button bounds by parsing the current hierarchy dump."""
        try:
            root = fromstring(d.dump_hierarchy())
        except Exception as e:
            self.logger.error(
                f"Failed to parse leave hierarchy: {e}"
            )
            return None, None

        for node in root.iter("node"):
            content_desc = node.attrib.get("content-desc", "")
            if content_desc == "Leave, button":
                return node.attrib.get("bounds"), content_desc

        return None, None

    def verify_zoom_installed(self):
        """Abort the test if the Zoom app is not installed on the device.

        Without this check the automation runs blind: app_start() shells out to
        monkey and ignores the failure, the meeting deep link opens in a browser
        instead, and the run only dies ~30s later with a misleading "name input
        screen not found" error.
        """
        try:
            output = self.adb_device.shell(f"pm list packages {ZOOM_PACKAGE}") or ""
        except Exception as e:
            self.logger.error(
                f"Could not query installed packages to confirm Zoom: {e}"
            )
            sys.exit(1)

        if f"package:{ZOOM_PACKAGE}" not in output.split():
            self.logger.error(
                f"Zoom app ({ZOOM_PACKAGE}) is not installed on this device. "
                f"Install Zoom on the device and re-run the test."
            )
            sys.exit(1)

        self.logger.info(f"Zoom app ({ZOOM_PACKAGE}) is installed.")

    def set_device(self, serial):
        """Set the target device for automation using its ADB serial number."""
        self.device_serial = serial
        try:
            self.adb_device = self.client.device(serial)
            if self.adb_device is None:
                raise Exception(f"Device with serial {serial} not found via ADB.")

            # Fail fast before the slow uiautomator2 connect if Zoom is missing.
            self.verify_zoom_installed()

            self.u2_device = u2.connect(serial)
            self.logger.info(f"Successfully connected to device {serial}.")

        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            raise

    def start_interop_app(self):
        """Force-stop Zoom and hand the device back to the interop app.

        The interop app is restarted with auto_start so it reconnects to
        LANforge on its own. Called from main()'s finally block, so the device
        is restored whether the run succeeded or failed.
        """
        if not self.adb_device:
            raise RuntimeError("Device not set. Call set_device() first.")
        self.logger.info("Launching Interop App...")
        self.adb_device.shell("am force-stop us.zoom.videomeetings")
        time.sleep(1)
        self.adb_device.shell("am force-stop com.candela.wecan")
        time.sleep(1)
        self.adb_device.shell(
            "am start --es auto_start 1 -n com.candela.wecan/com.candela.wecan.StartupActivity"
        )
        time.sleep(5)
        self.logger.info("Interop App launched successfully.")

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"{self.base_url}/check_stop"

            response = requests.get(endpoint_url, timeout=10)
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                if stop_signal_from_server:
                    self.stop_signal = True
                    self.logger.info(
                        "Stop signal received from the server. Exiting the Test."
                    )
            return self.stop_signal
        except Exception as e:
            self.logger.error(f"Error checking stop signal: {e}")
            return self.stop_signal

    def join_zoom_meeting(self, meeting_url, participant_name):
        """Drive one device through a full Zoom call, start to finish.

        Opens the meeting deep link, clears permission prompts, and types
        participant_name into either the preview screen or the older name dialog,
        whichever this Zoom build shows. Then enables audio and video, polls the
        host for the meeting end time, stays in the call until it passes or the
        server signals a stop, and leaves.
        """
        if not self.u2_device:
            raise RuntimeError("Device not set. Call set_device() first.")

        d = self.u2_device
        try:
            width, height = d.window_size()
        except Exception as e:
            # fallback defaults as it throws error in some devices
            width, height = 500, 1000
            self.logger.warning(
                f"Could not read window size ({e}); falling back to {width}x{height}."
            )
        tap_coords = (width // 2, height // 2)

        self._set_phase("LAUNCH")
        self.logger.info(f"Starting Zoom automation for {participant_name}.")
        self.logger.info(f"Screen {width}x{height}, centre tap at {tap_coords}.")

        self.logger.info(f"Starting {ZOOM_PACKAGE} and opening the meeting link.")
        d.app_start(ZOOM_PACKAGE, stop=True)
        time.sleep(2)

        self.adb_device.shell(
            f'am start -a android.intent.action.VIEW -d "{meeting_url}"'
        )
        self.logger.info(f"Meeting link handed to Zoom: {meeting_url}")
        time.sleep(8)

        self._set_phase("PERMISSIONS")
        self.logger.info("Checking for permission prompts.")
        allow_while_using = d(text="While using the app")
        if allow_while_using.wait(timeout=8):
            allow_while_using.click()
            self.logger.info("Granted 'While using the app'.")
            time.sleep(2)

            for permission_text in ["Allow", "ALLOW"]:
                allow_btn = d(text=permission_text, className="android.widget.Button")
                if allow_btn.wait(timeout=5):
                    allow_btn.click()
                    self.logger.info(f"Clicked '{permission_text}'.")
                    time.sleep(1)
        else:
            self.logger.info("No permission prompt appeared; already granted.")

        preview_join = d(text="Editing display name")
        if preview_join.wait(timeout=5):
            self.logger.info("Preview screen detected.")

            name_input = d(className="android.widget.EditText")
            if name_input.wait(timeout=10):
                self.logger.info(
                    f"Entering participant name: {participant_name}"
                )
                name_input.set_text(participant_name)
                time.sleep(1)
                ok_btn = d(text="OK")
                if ok_btn.wait(timeout=10):
                    ok_btn.click()
                    self.logger.info("Clicked 'OK' on preview screen.")
                else:
                    raise RuntimeError("'OK' button not found within 10 seconds on preview screen.")
            else:
                self.logger.error(
                    "Name input screen not found "
                    "(className='android.widget.EditText'). "
                    "Aborting automation."
                )
                raise RuntimeError(
                    "Could not find name input screen. "
                    "Zoom may not have launched correctly or the UI flow changed."
                )

            join_btn = d(text="Join")
            if join_btn.wait(timeout=10):
                join_btn.click()
                self.logger.info("Clicked 'Join' on preview screen.")
            else:
                raise RuntimeError("'Join' button not found within 10 seconds on preview screen.")

        else:
            # Old flow: check for name input screen
            name_input = d(resourceId="us.zoom.videomeetings:id/edtScreenName")
            if name_input.wait(timeout=15):
                self.logger.info(
                    f"Entering participant name: {participant_name}"
                )
                name_input.set_text(participant_name)
                time.sleep(1)
                ok_btn = d(text="OK", className="android.widget.Button")
                if ok_btn.wait(timeout=10):
                    ok_btn.click()
                else:
                    d(resourceId="us.zoom.videomeetings:id/button1").click()
                self.logger.info("Clicked 'Ok Button'")
            else:
                self.logger.error(
                    "Name input screen not found "
                    "(resourceId='us.zoom.videomeetings:id/edtScreenName'). "
                    "Aborting automation."
                )
                raise RuntimeError(
                    "Could not find name input screen. "
                    "Zoom may not have launched correctly or the UI flow changed."
                )

        self.logger.info("Waiting to join meeting...")
        time.sleep(10)

        self.reveal_zoom_controls(d, (width // 2, height // 2))

        leave_bounds, _leave_status = self.get_leave_control_info(d)
        if leave_bounds:
            self.logger.info(
                f"Successfully joined the meeting as {participant_name}."
            )
        else:
            self.logger.warning(
                "Leave button not found. Checking toolbar..."
            )
            if d(resourceId="us.zoom.videomeetings:id/panelMeetingToolbar").exists:
                self.logger.info(
                    "Found meeting toolbar - likely in meeting."
                )

        time.sleep(2)
        self.enable_audio_video(d, tap_coords=(width // 2, height // 2))
        time.sleep(2)
        count = 0
        while self.end_time is None:
            count += 1
            if count > 60:
                self.logger.error(
                    "Failed to retrieve meeting end time from server after 5 minutes. Leaving meeting."
                )
                sys.exit(1)
            try:
                self.get_start_and_end_time()
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Error fetching start/end time: {e}")
                time.sleep(5)
        self.logger.info(
            f"Meeting scheduled from {self.start_time} to {self.end_time}"
        )
        try:
            end_dt = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            if end_dt.tzinfo is None:
                end_dt = self.tz.localize(end_dt)
            else:
                end_dt = end_dt.astimezone(self.tz)
            meeting_end_dt = end_dt - timedelta(seconds=10)
        except Exception as e:
            raise RuntimeError(f"Invalid end_time received from server: {e}")

        # self.ping_monitor.start_ping(self.device_serial)
        while datetime.now(self.tz) < meeting_end_dt:
            if self.check_stop_signal():
                self.logger.info(
                    "Stop signal received. Leaving meeting early."
                )
                break
            time.sleep(2)

        try:
            self.reveal_zoom_controls(d, (width // 2, height // 2))

            self.logger.info("Leaving meeting...")
            leave_bounds, _leave_status = self.get_leave_control_info(d)
            if leave_bounds and self.tap_bounds_center(d, leave_bounds):
                time.sleep(2)
                leave_confirm = d(text="Leave meeting")
                if leave_confirm.wait(timeout=5):
                    leave_confirm.click()
                    self.logger.info("Confirmed leaving meeting.")
            else:
                self.logger.warning(
                    "Leave button not found. Pressing back..."
                )
                d.press("back")
                time.sleep(1)
                d.press("back")
        except Exception as e:
            self.logger.warning(
                f"Leave operation not executed, meeting might be ended from host side: {e}"
            )

    def get_start_and_end_time(self):
        """Fetch the meeting's start and end time from the host and store them.

        Sets self.start_time and self.end_time. On any failure it logs and
        leaves both unchanged, which is why the caller polls until they arrive.
        """
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                self.logger.error(
                    f"Failed to fetch start and end time. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")

    def enable_audio_video(self, d, max_retries=15, tap_coords=(500, 500)):
        """Continuously check and enable audio and video until both are enabled or retries exhausted."""
        self.logger.info("Ensuring audio and video are enabled...")

        retries = 0
        audio_enabled = False
        video_enabled = False

        while retries < max_retries and not (audio_enabled and video_enabled):
            retries += 1
            self.logger.info(f"Check attempt {retries}/{max_retries}")

            self.reveal_zoom_controls(d, tap_coords)
            if not audio_enabled:
                try:
                    audio_enabled_state, audio_bounds, audio_status = (
                        self.get_audio_control_info(d)
                    )
                    self.logger.info(f"Audio status: {audio_status}")

                    if audio_enabled_state is True:
                        self.logger.info("Audio already enabled")
                        audio_enabled = True
                    elif audio_enabled_state is False:
                        self.logger.info("Audio is disabled. Enabling...")
                        if self.tap_bounds_center(d, audio_bounds):
                            time.sleep(1)
                            (
                                audio_enabled_state,
                                _audio_bounds,
                                audio_status,
                            ) = self.get_audio_control_info(d)
                            self.logger.info(
                                f"Audio status after tap: {audio_status}"
                            )
                            if audio_enabled_state is True:
                                self.logger.info("Audio enabled")
                                audio_enabled = True
                        else:
                            self.logger.warning(
                                f"Audio button bounds missing: {audio_bounds}"
                            )
                    else:
                        join_audio = d(text="Join Audio")
                        if join_audio.exists:
                            self.logger.info(
                                "Audio prompt found. Joining audio..."
                            )
                            join_audio.click()
                            time.sleep(1)
                        else:
                            self.logger.warning("Audio button not visible")
                except Exception as e:
                    self.logger.error(f"Error checking audio: {e}")

            if not video_enabled:
                try:
                    video_enabled_state, video_bounds, video_status = (
                        self.get_video_control_info(d)
                    )
                    self.logger.info(f"Video status: {video_status}")

                    if video_enabled_state is True:
                        self.logger.info("Video already enabled")
                        video_enabled = True
                    elif video_enabled_state is False:
                        self.logger.info("Video is disabled. Enabling...")
                        if self.tap_bounds_center(d, video_bounds):
                            time.sleep(1)
                            (
                                video_enabled_state,
                                _video_bounds,
                                video_status,
                            ) = self.get_video_control_info(d)
                            self.logger.info(
                                f"Video status after tap: {video_status}"
                            )
                            if video_enabled_state is True:
                                self.logger.info("Video enabled")
                                video_enabled = True
                        else:
                            self.logger.warning(
                                f"Video button bounds missing: {video_bounds}"
                            )
                    else:
                        join_video = d(text="Join Video")
                        if join_video.exists:
                            self.logger.info(
                                "Video prompt found. Joining video..."
                            )
                            join_video.click()
                            time.sleep(1)
                        else:
                            self.logger.warning("Video button not visible")
                except Exception as e:
                    self.logger.error(f"Error checking video: {e}")

            time.sleep(2)

        if audio_enabled and video_enabled:
            self.logger.info("Both audio and video are enabled.")
        else:
            self.logger.warning(
                f"Could not fully enable audio/video after {max_retries} retries."
            )

    def upload_ping_log(self):
        """POST this participant's ping log to the host as a file upload.

        Warns and returns without uploading if PingMonitor never wrote the
        file, which is the case while the ping monitor is commented out.
        """
        log_path = os.path.join(self.log_dir, f"{self.participant_name}_ping.log")
        if not os.path.exists(log_path):
            self.logger.warning(f"Ping log not found: {log_path}")
            return

        endpoint_url = f"{self.base_url}/upload_ping_log"
        try:
            with open(log_path, "rb") as fp:
                files = {"file": (os.path.basename(log_path), fp, "text/plain")}
                data = {"participant_name": self.participant_name}
                resp = requests.post(endpoint_url, files=files, data=data, timeout=30)

            if resp.status_code == 200:
                self.logger.info(
                    "Ping log uploaded successfully"
                )
            else:
                self.logger.error(
                    f"Ping log upload failed: {resp.status_code} {resp.text}"
                )
        except Exception as e:
            self.logger.error(f"Error uploading ping log: {e}")

    def upload_log(self):
        """Push this run's log to the host's /upload_log endpoint.

        The server namespaces the saved filename by the current robo coordinate
        (and angle, if rotations are enabled) and archives it into the report
        folder at the end of the test — same mechanism used for the
        Windows/Linux/macOS real-device client logs.
        """
        log_path = os.path.join(self.log_dir, f"{self.participant_name}.log")
        if not os.path.exists(log_path):
            self.logger.warning(f"Log file not found: {log_path}")
            return

        endpoint_url = f"{self.base_url}/upload_log"
        try:
            with open(log_path, "r", errors="replace") as fp:
                log_content = fp.read()

            resp = requests.post(
                endpoint_url,
                json={"hostname": self.participant_name, "log": log_content},
                timeout=30,
            )

            if resp.status_code == 200:
                self.logger.info("Log uploaded successfully")
            else:
                self.logger.error(
                    f"Log upload failed: {resp.status_code} {resp.text}"
                )
        except Exception as e:
            self.logger.error(f"Error uploading log: {e}")


def main():
    """Parse the command line and run one device through the meeting.

    The log is uploaded and the interop app restarted in a finally block, so
    the device is handed back to LANforge even when the run fails.
    """
    parser = argparse.ArgumentParser(
        description="Automate joining a Zoom meeting on a single Android device."
    )
    parser.add_argument("--serial", help="ADB serial number of the target device")
    parser.add_argument("--meeting_url", help="Zoom meeting URL or deep link")
    parser.add_argument(
        "--participant_name", help="Name to use when joining the meeting"
    )
    parser.add_argument("--server_host", default="127.0.0.1", help="flask server host")
    parser.add_argument(
        "--server_port", type=int, default=5000, help="flask server port"
    )

    args = parser.parse_args()

    automator = ZoomAutomator(
        server_ip=args.server_host,
        server_port=args.server_port,
        participant_name=args.participant_name,
    )
    try:
        automator.set_device(args.serial)
        automator.join_zoom_meeting(args.meeting_url, args.participant_name)
    except Exception as e:
        automator.logger.error(f"Error: {e}")
    finally:
        try:
            automator.upload_log()
            # automator.upload_ping_log()
            automator.start_interop_app()
        except Exception as e:
            automator.logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
