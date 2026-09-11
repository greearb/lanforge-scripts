"""Drive VLC-for-Android through a multicast stream for LANforge interop tests."""

import argparse
import logging
import os
import subprocess
import sys
import time

import requests
import re

# Simple playback mode drives everything through plain adb, so a missing or
# broken uiautomator2 install must not stop VLC from launching.
try:
    import uiautomator2 as u2
    U2_AVAILABLE = True
    U2_IMPORT_ERROR = None
except Exception as _e:
    u2 = None
    U2_AVAILABLE = False
    U2_IMPORT_ERROR = _e

# Which copy of this file is running, since LANforge runs it on whatever
# resource has the phone attached -- not necessarily the orchestrator host.
SCRIPT_VERSION = "2026-09-11 (per-device logging, retries)"
print(f"[VERSION] vlc_android.py {SCRIPT_VERSION}")
print(f"[VERSION] running from: {os.path.abspath(__file__)}")
print(f"[VERSION] python: {sys.executable}")
print(f"[VERSION] uiautomator2 available: {U2_AVAILABLE}"
      + ("" if U2_AVAILABLE else f" ({U2_IMPORT_ERROR})"))


class VLCAndroidAutomation:
    VLC_PKG = "org.videolan.vlc"
    VLC_ACTIVITY = "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity"

    INTEROP_PKG = "com.candela.wecan"
    INTEROP_ACTIVITY = "com.candela.wecan/com.candela.wecan.StartupActivity"
    STATS_INTERVAL = 3
    U2_CONNECT_RETRIES = 3

    def __init__(self, serial, mcast_ip, port, duration, client_id=None, fserver=None, no_stats=False, simple=False):
        self.serial = serial
        self.mcast_ip = mcast_ip
        self.port = port
        self.duration = duration
        self.client_id = client_id
        self.fserver = fserver
        self.no_stats = no_stats
        self.uri = f"udp://@{mcast_ip}:{port}"

        self.simple = simple
        self.logger = self._create_logger()

        self.logger.info(f"client_id={client_id}, fserver={fserver}")
        if not simple and not U2_AVAILABLE:
            self.logger.warning(f"uiautomator2 unavailable ({U2_IMPORT_ERROR}) -- "
                                f"falling back to simple playback mode (adb only, no stats).")
            self.simple = True

        if self.simple:
            # Plain-adb mode: never touch uiautomator2 at all.
            self.d = None
        else:
            self.d = self._connect_u2(serial)

    # ---------------- Logging ----------------

    def _create_logger(self):
        """Per-device logger, writing to vlc_mobile_logs/<name>.log and stdout."""
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vlc_mobile_logs")
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir

        log_name = self.client_id or self.serial or "vlc_android"
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(log_name))
        logger_name = f"{__name__}.{safe_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

            file_handler = logging.FileHandler(
                os.path.join(log_dir, f"{safe_name}.log"), mode="w")
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

        return logger

    def _connect_u2(self, serial):
        """Connect to the device via uiautomator2, retrying transient failures."""
        last_err = None
        for attempt in range(1, self.U2_CONNECT_RETRIES + 1):
            try:
                self.logger.info(f"Connecting to device via uiautomator2 (attempt {attempt}/{self.U2_CONNECT_RETRIES})")
                return u2.connect(serial)
            except Exception as e:
                last_err = e
                self.logger.warning(f"uiautomator2 connect attempt {attempt} failed: {e}")
                time.sleep(2)
        raise RuntimeError(f"Could not connect to {serial} via uiautomator2 after "
                           f"{self.U2_CONNECT_RETRIES} attempts: {last_err}")

    # ---------------- ADB helpers ----------------

    def shell(self, cmd, timeout=10):
        self.logger.info(f">> shell: {cmd}")
        try:
            result = self.d.shell(cmd, timeout=timeout)
        except Exception as e:
            self.logger.error(f"[SHELL ERROR] {cmd}: {e}")
            raise
        if result.exit_code != 0:
            self.logger.error(f"[SHELL ERROR] {result.output}")
        return result.output

    # ---------------- VLC lifecycle ----------------

    def cleanup_vlc(self):
        self.logger.info("[VLC] Force stopping VLC")

        try:
            self.d.app_stop(self.VLC_PKG)
        except Exception as e:
            self.logger.warning(f"app_stop failed: {e}")

        self.shell(f"am force-stop {self.VLC_PKG}")
        self.shell(f"am kill {self.VLC_PKG}")

        # Kill any remaining process if possible
        try:
            pid = self.shell(f"pidof {self.VLC_PKG}").strip()
            if pid:
                self.shell(f"kill -9 {pid}")
        except Exception as e:
            self.logger.warning(f"Failed to kill VLC pid: {e}")

        try:
            tasks_output = self.shell("cmd activity list tasks")
            task_ids = set()
            for line in tasks_output.splitlines():
                if self.VLC_PKG in line:
                    match = re.search(r"taskId=(\d+)", line)
                    if match:
                        task_ids.add(match.group(1))
            for task_id in task_ids:
                self.shell(f"cmd activity task remove {task_id}")
        except Exception as e:
            self.logger.warning(f"Failed to remove VLC task: {e}")

        time.sleep(2)

    def launch_vlc(self):
        self.logger.info(f"[VLC] Launching VLC with URI: {self.uri}")
        self.shell(
            f'am start -a android.intent.action.VIEW '
            f'-d "{self.uri}" '
            f'-n {self.VLC_ACTIVITY}'
        )
        time.sleep(5)

    def parse_video_info(self, raw_text):
        parsed = {
            "demux_bitrate_kbps": None,
            "input_bitrate_kbps": None,
            "video_codec": None,
            "audio_codec": None,
            "channels": None,
            "sample_rate_hz": None,
            "framerate_fps": None,
            "elapsed_time_sec": None
        }

        i = 0
        while i < len(raw_text):
            key = raw_text[i].lower()

            try:
                val = raw_text[i + 1]
            except IndexError:
                break

            # --- BITRATES ---
            if key == "demux bitrate":
                parsed["demux_bitrate_kbps"] = self.extract_number(val)

            elif key == "input bitrate":
                parsed["input_bitrate_kbps"] = self.extract_number(val)

            # --- AUDIO ---
            elif key == "codec" and i > 0 and raw_text[i - 1].lower() == "audio":
                parsed["audio_codec"] = val

            elif key == "channels":
                parsed["channels"] = self.extract_number(val)

            elif key == "sample rate":
                parsed["sample_rate_hz"] = self.extract_number(val)

            # --- VIDEO ---
            elif key == "codec" and i > 0 and raw_text[i - 1].lower() == "video":
                parsed["video_codec"] = val

            # --- FRAMERATE ---
            elif "fps" in val.lower():
                parsed["framerate_fps"] = self.extract_number(val)

            # Bare "M:SS" token is VLC-Android's playback position -- used
            # below as the buffering/stall signal.
            elif parsed["elapsed_time_sec"] is None and re.match(r"^\d{1,2}:\d{2}$", raw_text[i].strip()):
                parsed["elapsed_time_sec"] = self._parse_mmss(raw_text[i].strip())

            i += 1

        return parsed

    @staticmethod
    def _parse_mmss(text):
        try:
            mins, secs = text.split(":")
            return int(mins) * 60 + int(secs)
        except Exception:
            return None

    def extract_video_info_stats(self):
        """Scroll through the Video Information screen, collecting all visible text."""
        stats = {
            "timestamp": time.time(),
            "raw_text": []
        }

        collected = []
        scrollable = self.d(scrollable=True)

        # Try to scroll to top first (safe even if already at top)
        try:
            scrollable.scroll.toBeginning(max_swipes=2)
            time.sleep(0.5)
        except Exception:
            pass

        for _ in range(6):  # max scroll depth safety limit
            # Not deduplicated by text value -- "Codec" legitimately appears twice
            # (Video, then Audio), and parse_video_info relies on that order.
            page = [
                el.attrib.get("text", "").strip()
                for el in self.d.xpath('//*').all()
                if el.attrib.get("text", "").strip()
            ]

            new_tail = self._new_suffix(collected, page)
            if not new_tail:
                break
            collected.extend(new_tail)

            # Try scrolling down
            try:
                if not scrollable.scroll.forward():
                    break
                time.sleep(0.5)
            except Exception:
                break

        stats["raw_text"] = collected
        return stats

    @staticmethod
    def _new_suffix(collected, page):
        """Return the part of `page` not already at the end of `collected` (i.e. what scrolling revealed)."""
        if not collected:
            return page
        for overlap in range(min(len(collected), len(page)), 0, -1):
            if collected[-overlap:] == page[:overlap]:
                return page[overlap:]
        return page

    def collect_video_stats(self):
        self.logger.info("[STATS] Collecting video information stats")
        stats_list = []

        # VLC-Android has no frame/buffer-loss counter, only playback
        # position -- if it advances much slower than real time between two
        # polls, that's treated as a stall (not an exact frame-drop count).
        prev_elapsed_sec = None
        prev_poll_time = None
        stall_count = 0

        start = time.time()
        while time.time() - start < self.duration:
            try:
                snap = self.extract_video_info_stats()
                parsed = self.parse_video_info(snap["raw_text"])

                possible_stall = None
                elapsed_sec = parsed.get("elapsed_time_sec")
                if elapsed_sec is not None and prev_elapsed_sec is not None:
                    wall_delta = snap["timestamp"] - prev_poll_time
                    played_delta = elapsed_sec - prev_elapsed_sec
                    # Some slack: position ticks in whole seconds and polls
                    # aren't perfectly periodic, so only flag a clear stall.
                    possible_stall = wall_delta > 0.5 and played_delta < (wall_delta * 0.5)
                    if possible_stall:
                        stall_count += 1
                if elapsed_sec is not None:
                    prev_elapsed_sec = elapsed_sec
                    prev_poll_time = snap["timestamp"]

                parsed["possible_stall"] = possible_stall
                parsed["stall_events_so_far"] = stall_count

                combined = {
                    "timestamp": snap["timestamp"],
                    "raw": snap["raw_text"],
                    "parsed": parsed,
                    "device_type": "Android"
                }

                stats_list.append(combined)

                self.logger.info(f"[STATS PARSED] {parsed}")
                if self.client_id and self.fserver:
                    self.report_starts_to_server(
                        combined,
                        client_id=self.client_id,
                        server_url=self.fserver+"/stats" if self.fserver else None
                    )
            except Exception as e:
                self.logger.warning(f"Failed to collect stats: {e}")

            time.sleep(self.STATS_INTERVAL)

        return stats_list

    def report_starts_to_server(self, stats, client_id="client1", server_url="http://0.0.0.0:5959/stats"):
        self.logger.info(f"[REPORT] Reporting stats to server at {server_url}")
        try:
            payload = {
                client_id: stats
            }
            res = requests.post(server_url, json=payload)
            self.logger.info(f"Sent stats: {res.status_code}")
        except Exception as e:
            self.logger.error(f"Error sending stats to server: {e}")

    # ---------------- UI helpers ----------------

    def reveal_overlay(self):
        w, h = self.d.window_size()
        self.logger.info("[VLC] Tapping center once to reveal overlay")
        self.d.click(w // 2, h // 2)
        time.sleep(1)

        three_dot = self.d(resourceId="org.videolan.vlc:id/player_overlay_adv_function")
        if three_dot.exists:
            self.logger.info("[VLC] Overlay revealed successfully")
            return True

        self.logger.error("[ERROR] Overlay reveal failed")
        return False

    def print_full_hierarchy(self, tag=""):
        self.logger.info(f"[DEBUG] FULL UI HIERARCHY {tag}")
        xml = self.d.dump_hierarchy(compressed=False)
        self.logger.info(xml)

    def open_video_information(self):
        self.logger.info("[VLC] Looking for three-dot menu button")

        three_dot = self.d(resourceId="org.videolan.vlc:id/player_overlay_adv_function")

        if not three_dot.exists:
            if not self.reveal_overlay():
                self.logger.error("[ERROR] Three-dot menu not found - VLC not fully initialized")
                return False

        self.logger.info("[VLC] Three-dot menu found - clicking")
        three_dot.click()
        time.sleep(1)

        self.logger.info("[VLC] Looking for 'Video information' option")
        video_info = self.d(text="Video information")

        if video_info.wait(timeout=5):
            self.logger.info("[VLC] Clicking 'Video information'")
            video_info.click()
            time.sleep(2)
            self.logger.info("[VLC] Video information screen opened successfully")
            return True

        self.logger.error("[ERROR] 'Video information' not found in menu")
        return False

    def launch_interop(self):
        self.logger.info("[INTEROP] Launching interop app")
        if self.simple:
            # self.shell() goes through uiautomator2, which simple mode never
            # connects to -- use adb directly instead.
            self.adb(["shell", "am", "start", "--es", "auto_start", "1",
                      "-n", self.INTEROP_ACTIVITY])
        else:
            self.shell(f"am start --es auto_start 1 -n {self.INTEROP_ACTIVITY}")

    def extract_number(self, text):
        match = re.search(r"([\d.]+)", text)
        return float(match.group(1)) if match else None

    # ---------------- Main execution ----------------

    def ensure_screen_awake(self):
        """Wake and confirm the screen is on -- a sleeping/locked screen leaves nothing for uiautomator2 to use."""
        self.logger.info("[VLC] Ensuring screen is awake")
        try:
            self.shell("input keyevent KEYCODE_WAKEUP")
            time.sleep(1)
            power_state = self.shell("dumpsys power")
            awake = "mWakefulness=Awake" in power_state
            if not awake:
                self.logger.warning("Screen did not wake. If this device has a PIN/pattern/"
                                    "swipe lock, disable it for testing (adb can wake a screen but "
                                    "shouldn't be relied on to bypass a real lock).")
            return awake
        except Exception as e:
            self.logger.warning(f"Failed to check/wake screen: {e}")
            return False

    def adb(self, args, timeout=20):
        """Run an adb command against this device, independent of uiautomator2."""
        cmd = ["adb", "-s", self.serial] + args
        self.logger.info(f">> adb: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if res.returncode != 0:
                self.logger.error(f"[ADB ERROR] {res.stderr.strip()}")
            return res.stdout
        except Exception as e:
            self.logger.error(f"[ADB ERROR] {e}")
            return ""

    def read_wlan_rx_bytes(self, iface="wlan0"):
        """Total bytes received on the phone's WiFi interface, read from /proc/net/dev."""
        out = self.adb(["shell", "cat", "/proc/net/dev"])
        for line in out.splitlines():
            line = line.strip()
            if line.startswith(iface + ":"):
                fields = line.split(":", 1)[1].split()
                if fields:
                    try:
                        return int(fields[0])  # RX bytes is the first column
                    except ValueError:
                        return None
        return None

    def collect_simple_stats(self):
        """Sample wlan0 RX bytes (as a bitrate) and VLC foreground state over adb, since
        VLC's decode counters need uiautomator2. Not stream-isolated -- counts all wlan0 traffic."""
        self.logger.info("[SIMPLE] Sampling network stats over adb")
        stats_list = []
        prev_bytes = self.read_wlan_rx_bytes()
        prev_time = time.time()

        start = time.time()
        while time.time() - start < self.duration:
            time.sleep(self.STATS_INTERVAL)
            try:
                now_bytes = self.read_wlan_rx_bytes()
                now_time = time.time()

                kbps = None
                if now_bytes is not None and prev_bytes is not None and now_time > prev_time:
                    delta = now_bytes - prev_bytes
                    if delta >= 0:
                        kbps = round((delta * 8 / 1000) / (now_time - prev_time), 1)

                focus = self.adb(["shell", "dumpsys", "window"])
                playing = self.VLC_PKG in focus

                parsed = {
                    "input_bitrate_kbps": kbps,
                    "demux_bitrate_kbps": None,
                    "video_codec": "N/A (no UI scrape)",
                    "audio_codec": "N/A (no UI scrape)",
                    "channels": None,
                    "sample_rate_hz": None,
                    "framerate_fps": None,
                    "rx_bytes_total": now_bytes,
                    "vlc_in_foreground": playing,
                }

                combined = {
                    "timestamp": now_time,
                    "raw": [],
                    "parsed": parsed,
                    "device_type": "Android",
                }
                stats_list.append(combined)
                self.logger.info(f"[SIMPLE STATS] rx={kbps} kb/s  vlc_foreground={playing}")

                if self.client_id and self.fserver:
                    self.report_starts_to_server(
                        combined,
                        client_id=self.client_id,
                        server_url=self.fserver + "/stats",
                    )

                prev_bytes, prev_time = now_bytes, now_time
            except Exception as e:
                self.logger.warning(f"simple stats sample failed: {e}")

        return stats_list

    def run_simple(self):
        """Playback-only mode: wake the screen, launch VLC on the multicast URL, let it play, clean up. adb only, no uiautomator2."""
        self.logger.info("[SIMPLE] Playback-only mode (adb only, no stats)")

        # Confirm the device is actually reachable before anything else.
        state = self.adb(["get-state"]).strip()
        self.logger.info(f"[SIMPLE] adb get-state -> {state!r}")
        if state != "device":
            raise RuntimeError(
                f"adb reports device state {state!r} for serial {self.serial} -- "
                f"the phone is not reachable from this machine. Check 'adb devices -l' "
                f"and that USB debugging is authorized."
            )

        self.adb(["shell", "am", "force-stop", self.VLC_PKG])
        self.adb(["shell", "input", "keyevent", "KEYCODE_WAKEUP"])
        time.sleep(1)

        wake = self.adb(["shell", "dumpsys", "power"])
        if "mWakefulness=Awake" not in wake:
            self.logger.warning("Screen may not be awake. If this device has a lock screen, "
                                "disable it (Settings > Security > Screen lock > None) and run "
                                "'adb shell svc power stayon true'.")

        self.logger.info(f"[SIMPLE] Launching VLC on {self.uri}")
        self.adb([
            "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", self.uri,
            "-n", self.VLC_ACTIVITY,
        ])
        time.sleep(5)

        focus = self.adb(["shell", "dumpsys", "window"])
        if self.VLC_PKG in focus:
            self.logger.info("[SIMPLE] VLC is in the foreground -- playback started.")
        else:
            self.logger.warning("VLC does not appear to be in the foreground. It may have "
                                "failed to launch; check that VLC is installed on the device.")

        self.logger.info(f"[SIMPLE] Letting VLC play for {self.duration} seconds")
        if self.no_stats or not (self.client_id and self.fserver):
            time.sleep(self.duration)
        else:
            self.collect_simple_stats()

        self.adb(["shell", "am", "force-stop", self.VLC_PKG])
        self.logger.info("[SIMPLE] Done.")

    def run(self):
        if self.simple:
            return self.run_simple()

        # Pre-cleanup
        self.cleanup_vlc()
        time.sleep(1)

        # Warn, don't abort -- the wake check can fail for benign reasons and
        # playback may still work, so it must never block VLC from launching.
        if not self.ensure_screen_awake():
            self.logger.warning("Screen did not report as awake -- continuing anyway. If playback "
                                "does not appear, the device is likely locked: disable the screen lock "
                                "(Settings > Security > Screen lock > None) and run "
                                "'adb shell svc power stayon true'.")

        # Launch VLC
        self.launch_vlc()
        # Extra settle time beyond launch_vlc()'s own wait -- manual testing
        # showed the activity isn't reliably interactive right at that point.
        time.sleep(3)

        # Try revealing overlay
        tries = 0
        while tries < 5:
            tries += 1
            try:
                if self.reveal_overlay():
                    break
                self.logger.warning(f"Overlay reveal attempt {tries}/5 failed, retrying...")
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Exception during overlay reveal: {e}")
                time.sleep(1)

        # Open Video Information
        success = self.open_video_information()

        if success:
            self.logger.info("[PASS] VLC playback verified via Video Information")
        else:
            self.logger.error("[FAIL] VLC playback verification failed")

        # Let VLC run. If Video Information never opened, skip stat scraping
        # rather than scroll the playback screen and disturb the video.
        self.logger.info(f"[INFO] Letting VLC run for {self.duration} seconds")
        if success and not self.no_stats:
            self.collect_video_stats()
        else:
            if self.no_stats:
                self.logger.info("--no_stats set: letting playback run without UI scraping.")
            else:
                self.logger.info("Video Information never opened -- skipping stats scraping "
                                 "so the UI gestures don't disturb playback.")
            time.sleep(self.duration)

        # Post-cleanup
        self.cleanup_vlc()
        self.logger.info("[DONE] VLC UI automation finished cleanly")


def main():
    parser = argparse.ArgumentParser(description="VLC Android UI automation")
    parser.add_argument("--serial", required=True)
    parser.add_argument("--mcast_ip", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--duration", type=int, required=True)
    parser.add_argument("--client_id")
    parser.add_argument("--fserver")
    parser.add_argument("--simple", action="store_true",
                        help="Playback-only mode using plain adb: no uiautomator2, no UI "
                             "gestures, no stats. The most reliable way to just get the "
                             "stream playing on a phone.")
    parser.add_argument("--no_stats", action="store_true",
                        help="Play the stream without scraping the Video Information panel. "
                             "The scraping gestures can disturb playback -- use this when "
                             "smooth playback matters more than per-device stats.")

    args = parser.parse_args()
    fserver = f"http://{args.fserver}" if args.fserver else None

    try:
        vlc = VLCAndroidAutomation(
            serial=args.serial,
            mcast_ip=args.mcast_ip,
            port=args.port,
            duration=args.duration,
            client_id=args.client_id,
            fserver=fserver,
            no_stats=args.no_stats,
            simple=args.simple
        )
        vlc.logger.info(f"server received: {vlc.fserver} {args.fserver}")
        vlc.run()
        vlc.launch_interop()
    except Exception as e:
        # Report the failure to the collector. Uses requests directly (not
        # vlc.report_starts_to_server) since construction itself may be what failed.
        print(f"[FATAL] vlc_android.py failed: {e}")
        if args.client_id and fserver:
            try:
                requests.post(
                    fserver + "/stats",
                    json={args.client_id: {
                        "timestamp": time.time(),
                        "device_type": "Android",
                        "automation_failed": True,
                        "error": str(e),
                    }}
                )
            except Exception as post_err:
                print(f"[WARN] Couldn't even report the failure: {post_err}")
        raise


if __name__ == "__main__":
    main()
