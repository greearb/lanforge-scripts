from datetime import datetime, timedelta
import uiautomator2 as u2
import time
import argparse
import re
import xml.etree.ElementTree as ET
from ppadb.client import Client as AdbClient
import requests
import pytz


class ZoomAutomator:
    def __init__(
        self, host="127.0.0.1", port=5037, server_ip="127.0.0.1", server_port=5000
    ):
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

    @staticmethod
    def _parse_bounds(bounds):
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
        if not match:
            return None
        return tuple(map(int, match.groups()))

    def tap_bounds_center(self, d, bounds):
        parsed = self._parse_bounds(bounds)
        if not parsed:
            return False

        left, top, right, bottom = parsed
        d.click((left + right) // 2, (top + bottom) // 2)
        return True

    def reveal_zoom_controls(self, d, tap_coords):
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
            root = ET.fromstring(d.dump_hierarchy())
        except Exception as e:
            print(f"[{self.device_serial}] Failed to parse audio hierarchy: {e}")
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
            root = ET.fromstring(d.dump_hierarchy())
        except Exception as e:
            print(f"[{self.device_serial}] Failed to parse video hierarchy: {e}")
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
            root = ET.fromstring(d.dump_hierarchy())
        except Exception as e:
            print(f"[{self.device_serial}] Failed to parse leave hierarchy: {e}")
            return None, None

        for node in root.iter("node"):
            content_desc = node.attrib.get("content-desc", "")
            if content_desc == "Leave, button":
                return node.attrib.get("bounds"), content_desc

        return None, None

    def set_device(self, serial):
        """Set the target device for automation using its ADB serial number."""
        self.device_serial = serial
        try:
            # Get the device object via ADB client
            self.adb_device = self.client.device(serial)
            if self.adb_device is None:
                raise Exception(f"Device with serial {serial} not found via ADB.")

            # Connect using uiautomator2 for UI interaction
            self.u2_device = u2.connect(serial)
            print(f"[{serial}] Successfully connected to device.")

        except Exception as e:
            print(f"[{serial}] Failed to connect: {e}")
            raise

    def start_interop_app(self):
        if not self.adb_device:
            raise RuntimeError("Device not set. Call set_device() first.")
        print(f"[{self.device_serial}] Launching Interop App...")
        self.adb_device.shell("am force-stop us.zoom.videomeetings")
        time.sleep(1)
        self.adb_device.shell("am force-stop com.candela.wecan")
        time.sleep(1)
        self.adb_device.shell(
            "am start --es auto_start 1 -n com.candela.wecan/com.candela.wecan.StartupActivity"
        )
        time.sleep(5)
        print(f"[{self.device_serial}] Interop App launched successfully.")

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"{self.base_url}/check_stop"

            response = requests.get(endpoint_url)  # Replace with your Flask server URL
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    print("Stop signal received from the server. Exiting the loop.")
                else:

                    print("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            print(f"Error checking stop signal: {e}")

    def join_zoom_meeting(self, meeting_url, participant_name):
        if not self.u2_device:
            raise RuntimeError("Device not set. Call set_device() first.")

        serial = self.device_serial
        d = self.u2_device
        try:
            width, height = d.window_size()
        except Exception:
            # fallback defaults as it throws error in some devices
            width, height = 500, 1000

        print(f"[{serial}] Starting Zoom automation for: {participant_name}")

        # 1. Launch Zoom using the meeting link
        print(f"[{serial}] Launching Zoom app with meeting link...")
        d.app_start("us.zoom.videomeetings", stop=True)
        time.sleep(2)

        self.adb_device.shell(
            f'am start -a android.intent.action.VIEW -d "{meeting_url}"'
        )
        time.sleep(8)

        # 2. Handle permission prompts first
        print(f"[{serial}] Checking for permission prompts...")
        allow_while_using = d(text="While using the app")
        if allow_while_using.wait(timeout=8):
            allow_while_using.click()
            print(f"[{serial}] Granted 'While using the app' permission")
            time.sleep(2)

            for permission_text in ["Allow", "ALLOW"]:
                allow_btn = d(text=permission_text, className="android.widget.Button")
                if allow_btn.wait(timeout=5):
                    allow_btn.click()
                    print(f"[{serial}] Clicked {permission_text}")
                    time.sleep(1)

        # 3. Detect preview screen
        preview_join = d(text="Editing display name")
        if preview_join.wait(timeout=5):
            print(f"[{serial}] Preview screen detected.")

            # Enter name if field is present
            name_input = d(className="android.widget.EditText")
            if name_input.exists:
                print(f"[{serial}] Entering participant name: {participant_name}")
                name_input.set_text(participant_name)
                time.sleep(1)
                d(text="OK").click()
                print(f"[{serial}] Clicked 'Join' on preview screen.")
            # Tap join on preview
            d(text="Join").click()
            print(f"[{serial}] Clicked 'Join' on preview screen.")

        else:
            # 4. Old flow: check for name input screen
            name_input = d(resourceId="us.zoom.videomeetings:id/edtScreenName")
            if name_input.wait(timeout=15):
                print(f"[{serial}] Entering participant name: {participant_name}")
                name_input.set_text(participant_name)
                time.sleep(1)
                ok_btn = d(text="OK", className="android.widget.Button")
                if ok_btn.exists:
                    ok_btn.click()
                else:
                    d(resourceId="us.zoom.videomeetings:id/button1").click()
                print(f"[{serial}] Clicked 'Ok Button'")
            else:
                print(f"[{serial}] Name input screen not found. Proceeding...")

        # 5. Wait to join the meeting
        print(f"[{serial}] Waiting to join meeting...")
        time.sleep(10)

        # Reveal controls before checking meeting state or toggles.
        self.reveal_zoom_controls(d, (width // 2, height // 2))

        # 6. Check if in meeting
        leave_bounds, _leave_status = self.get_leave_control_info(d)
        if leave_bounds:
            print(f"[{serial}] Successfully joined the meeting as {participant_name}.")
        else:
            print(f"[{serial}] Warning: Leave button not found. Checking toolbar...")
            if d(resourceId="us.zoom.videomeetings:id/panelMeetingToolbar").exists:
                print(f"[{serial}] Found meeting toolbar — likely in meeting.")

        time.sleep(2)
        self.enable_audio_video(d, tap_coords=(width // 2, height // 2))
        time.sleep(2)
        while self.end_time is None:
            try:
                self.get_start_and_end_time()
                time.sleep(2)
            except Exception as e:
                print(f"[{serial}] Error fetching start/end time: {e}")
                time.sleep(5)
        print(f"[{serial}] Meeting scheduled from {self.start_time} to {self.end_time}")
        while (
            datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
            < (
                datetime.fromisoformat(self.end_time) - timedelta(seconds=10)
            ).isoformat()
        ):
            if self.check_stop_signal():
                print(f"[{serial}] Stop signal received. Leaving meeting early.")
                break
            time.sleep(2)

        # 7. Stay in the meeting
        try:
            self.reveal_zoom_controls(d, (width // 2, height // 2))

            # 8. Leave the meeting
            print(f"[{serial}] Leaving meeting...")
            leave_bounds, _leave_status = self.get_leave_control_info(d)
            if leave_bounds and self.tap_bounds_center(d, leave_bounds):
                time.sleep(2)
                leave_confirm = d(text="Leave meeting")
                if leave_confirm.wait(timeout=5):
                    leave_confirm.click()
                    print(f"[{serial}] Confirmed leaving meeting.")
            else:
                print(f"[{serial}] Leave button not found. Pressing back...")
                d.press("back")
                time.sleep(1)
                d.press("back")
        except Exception as e:
            print(
                f"Leave operation not executed, meeting might be ended from host side: {e}"
            )

    def get_start_and_end_time(self):
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                print(
                    f"Failed to fetch start and end time. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def enable_audio_video(self, d, max_retries=15, tap_coords=(500, 500)):
        """
        Continuously check and enable audio and video until both are enabled or retries exhausted.
        """
        serial = self.device_serial
        print(f"[{serial}] Ensuring audio and video are enabled...")

        retries = 0
        audio_enabled = False
        video_enabled = False

        while retries < max_retries and not (audio_enabled and video_enabled):
            retries += 1
            print(f"[{serial}] Check attempt {retries}/{max_retries}")

            self.reveal_zoom_controls(d, tap_coords)
            if not audio_enabled:
                # --- AUDIO check ---
                try:
                    audio_enabled_state, audio_bounds, audio_status = (
                        self.get_audio_control_info(d)
                    )
                    print(f"[{serial}] Audio status: {audio_status}")

                    if audio_enabled_state is True:
                        print(f"[{serial}] Audio already enabled")
                        audio_enabled = True
                    elif audio_enabled_state is False:
                        print(f"[{serial}] Audio is disabled. Enabling...")
                        if self.tap_bounds_center(d, audio_bounds):
                            time.sleep(1)
                            (
                                audio_enabled_state,
                                _audio_bounds,
                                audio_status,
                            ) = self.get_audio_control_info(d)
                            print(f"[{serial}] Audio status after tap: {audio_status}")
                            if audio_enabled_state is True:
                                print(f"[{serial}] Audio enabled")
                                audio_enabled = True
                        else:
                            print(
                                f"[{serial}] Audio button bounds missing: {audio_bounds}"
                            )
                    else:
                        join_audio = d(text="Join Audio")
                        if join_audio.exists:
                            print(f"[{serial}] Audio prompt found. Joining audio...")
                            join_audio.click()
                            time.sleep(1)
                        else:
                            print(f"[{serial}] Audio button not visible")
                except Exception as e:
                    print(f"[{serial}] Error checking audio: {e}")

            # --- VIDEO check ---
            if not video_enabled:
                try:
                    video_enabled_state, video_bounds, video_status = (
                        self.get_video_control_info(d)
                    )
                    print(f"[{serial}] Video status: {video_status}")

                    if video_enabled_state is True:
                        print(f"[{serial}] Video already enabled")
                        video_enabled = True
                    elif video_enabled_state is False:
                        print(f"[{serial}] Video is disabled. Enabling...")
                        if self.tap_bounds_center(d, video_bounds):
                            time.sleep(1)
                            (
                                video_enabled_state,
                                _video_bounds,
                                video_status,
                            ) = self.get_video_control_info(d)
                            print(f"[{serial}] Video status after tap: {video_status}")
                            if video_enabled_state is True:
                                print(f"[{serial}] Video enabled")
                                video_enabled = True
                        else:
                            print(
                                f"[{serial}] Video button bounds missing: {video_bounds}"
                            )
                    else:
                        join_video = d(text="Join Video")
                        if join_video.exists:
                            print(f"[{serial}] Video prompt found. Joining video...")
                            join_video.click()
                            time.sleep(1)
                        else:
                            print(f"[{serial}] Video button not visible")
                except Exception as e:
                    print(f"[{serial}] Error checking video: {e}")

            time.sleep(2)

        if audio_enabled and video_enabled:
            print(f"[{serial}] Both audio and video are enabled.")
        else:
            print(
                f"[{serial}]Could not fully enable audio/video after {max_retries} retries."
            )


def main():
    parser = argparse.ArgumentParser(
        description="Automate joining a Zoom meeting on a single Android device."
    )
    parser.add_argument("--serial", help="ADB serial number of the target device")
    parser.add_argument("--meeting_url", help="Zoom meeting URL or deep link")
    parser.add_argument(
        "--participant_name", help="Name to use when joining the meeting"
    )
    parser.add_argument("--server_host", default="0.0.0.0", help="flask server host")
    parser.add_argument(
        "--server_port", type=int, default=5000, help="flask server port"
    )

    args = parser.parse_args()

    automator = ZoomAutomator(server_ip=args.server_host, server_port=args.server_port)
    try:
        automator.set_device(args.serial)
        automator.join_zoom_meeting(args.meeting_url, args.participant_name)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            automator.start_interop_app()
        except Exception as e:
            print(f"Error starting interop app: {e}")


if __name__ == "__main__":
    main()
