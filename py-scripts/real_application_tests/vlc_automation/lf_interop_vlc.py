#!/usr/bin/env python3
"""
NAME: lf_interop_vlc.py

PURPOSE:
lf_interop_vlc.py sets up a VLC media streaming interoperability test using LANforge.
It streams video -- from a clustered host device, from this LANforge machine itself
(--host_media), or from an external/WAN source (--external_source) -- to multiple
Windows/Linux/macOS/Android client devices over Wi-Fi multicast, and reports per-device
playback stats (frames displayed/lost, bitrate, buffering events).

EXAMPLE-1:
Stream a video from a specific clustered host resource to the selected clients:
python3 lf_interop_vlc.py --video_name 'C:\\Users\\Administrator\\Downloads\\sample.mp4' --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --host_res 1.13 --server_ip 192.168.0.57

EXAMPLE-2:
Same, but let the script pick the first non-Android selected device as host:
python3 lf_interop_vlc.py --video_name 'C:\\Users\\Administrator\\Downloads\\sample.mp4' --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --server_ip 192.168.0.57

EXAMPLE-3:
Run with every selected device as a client only (no host is started):
python3 lf_interop_vlc.py --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --server_ip 192.168.0.57

EXAMPLE-4:
Nokia/WAN-hosted external multicast source -- guarantees no clustered device is ever
picked as host, even if --host_res/--video_name are also passed:
python3 lf_interop_vlc.py --duration 300 --mcast_addr 239.255.0.1 --mcast_port 1234 --server_ip 192.168.0.57 --external_source

EXAMPLE-5:
Host two media files locally on this LANforge machine, rotating between them every 60s
(--host_media/--host_iface/--host_rotate), with laptop clients in simple playback mode
(--client_simple) and Android clients in simple/no-UI mode (--android_simple):
python3 lf_interop_vlc.py --mgr 192.168.207.75 --server_ip 192.168.207.75 \
    --mcast_addr 239.255.0.1 --mcast_port 1234 \
    --host_media "/home/lanforge/QA_TEST_VIDEO.mp4,/home/lanforge/testvideo.mp4" \
    --host_iface eth1 --host_rotate --client_script_dir /Users/lanforge --client_simple \
    --switch_mode time --switch_value 60 --external_source --android_simple --duration 120

SCRIPT_CLASSIFICATION: Test

NOTES:
1. Use './lf_interop_vlc.py --help' to see full command line usage and options.
2. --duration and --switch_value (in "time" switch mode) are both in seconds.
3. If --host_res/--video_name/devices aren't given, the script interactively lists
   available resources and prompts you to select which ones to use.
4. --external_source and --host_media are independent: --external_source only controls
   whether a clustered resource is picked as host; --host_media additionally makes this
   LANforge machine itself serve the stream, so the two are commonly used together.
"""

import sys
import os
import threading
import time
import importlib
import logging
import argparse
import subprocess
import struct
from datetime import datetime, timedelta
import pandas as pd
import requests
from tabulate import tabulate
from flask import Flask, request, jsonify
import socket

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report


lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph_horizontal = lf_graph.lf_bar_graph_horizontal

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


class VLCStream(Realm):
    def __init__(self,
                 manager_ip=None,
                 port=8080,
                 mcast_addr="239.255.0.1",
                 mcast_port="1234",
                 host_res=None,
                 video_name=None,
                 duration=60,
                 fserver="localhost",
                 fport=5959,
                 extra_streams=None,
                 switch_mode="time",
                 switch_value=30,
                 external_source=False,
                 adb_map=None,
                 android_no_stats=False,
                 android_simple=False,
                 host_media=None,
                 host_iface=None,
                 host_gui=False,
                 host_vb=None,
                 host_rotate=False,
                 android_script=None,
                 client_script_dir=None,
                 client_simple=False,
                 _debug_on=False):
        super().__init__(lfclient_host=manager_ip,
                         debug_=_debug_on)
        self.manager_ip = manager_ip
        self.manager_port = port
        self.devices_data = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'generic'
        self.generic_endps_profile.cmd = ' '
        self.result_json = {}
        self.stop_time = None
        self.start_time = None
        self.mcast_addr = mcast_addr
        self.mcast_port = mcast_port
        self.host_res = host_res
        self.video_name = video_name
        self.duration = duration
        self.fserver = fserver
        self.fport = fport
        # Extra (ip, port) streams beyond mcast_addr/mcast_port for laptop-client
        # switching -- 0 to 4 entries (5 streams total max).
        self.extra_streams = extra_streams or []
        self.switch_mode = switch_mode
        self.switch_value = switch_value
        # True for Nokia/WAN-hosted sources: no device from this run's pool is
        # ever selected as host (see get_resource_data).
        self.external_source = external_source
        # Manual ANDROID_RESOURCE_ID -> adb_id overrides (see get_resource_data).
        self.adb_map = adb_map or {}
        # Skip Android UI stat-scraping -- the gestures can disturb playback.
        self.android_no_stats = android_no_stats
        # Playback-only Android mode: plain adb, no uiautomator2, no stats.
        self.android_simple = android_simple
        # Local multicast hosting on this machine (LANforge), so one command
        # both serves the streams and runs the client test.
        self.host_media = host_media or []
        # Accept several interfaces since one can only reach its own subnet
        # (e.g. laptops on one, phones on another).
        if isinstance(host_iface, str):
            self.host_ifaces = [i.strip() for i in host_iface.split(",") if i.strip()]
        else:
            self.host_ifaces = list(host_iface or [])
        self.host_iface = self.host_ifaces[0] if self.host_ifaces else None
        self.host_gui = host_gui
        self.host_vb = host_vb
        self.host_procs = []
        # Host-side rotation: play each media file in turn on the SAME group,
        # stopping one before the next -- works even on Android, which can't switch client-side.
        self.host_rotate = host_rotate
        # Absolute path to vlc_android.py -- a relative path can resolve against
        # LANforge's working dir and run a stale copy. Defaults to the copy beside this script.
        self.android_script = android_script or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "vlc_android.py")
        # Directory holding ctvlc.py/ctvlc.bash on the laptop clients -- needed since
        # LANforge runs generic endpoints from its own working dir, not the script's.
        self.client_script_dir = (client_script_dir or "").rstrip("/")
        # Laptop clients play only -- no RC socket, no stats.
        self.client_simple = client_simple
        self.rotate_stop = threading.Event()
        self.rotate_thread = None
        self.current_media_idx = 0
        self.app = Flask(__name__)
        self.stats = {}
        self.transitions = {}
        self.android_errors = {}

    def get_port_data(self, resource_data):
        # Only returns real device ports that are not phantom and are up.
        # TODO: add an option to also detect down ports.
        resource_id = list(resource_data.keys())
        ports = self.json_get('/ports/all')['interfaces']
        matched_resources = set()
        for port_data_dict in ports:
            port_id = list(port_data_dict.keys())[0]
            port_id_parts = port_id.split('.')
            resource = port_id_parts[0] + '.' + port_id_parts[1]

            # Skip any non-real devices we have decided to not track
            if resource not in resource_id:
                continue

            # Need to unpack resource data dict of encapsulating dict that contains it
            port_data_dict = port_data_dict[port_id]

            if 'phantom' not in port_data_dict or 'down' not in port_data_dict or 'parent dev' not in port_data_dict:
                logger.error('Malformed json response for endpoint /ports/all')
                raise ValueError('Malformed json response for endpoint /ports/all')

            # Skip phantom or down ports
            if port_data_dict['phantom'] or port_data_dict['down']:
                continue

            # TODO: Support more than one station per real device
            if port_data_dict['parent dev'] != 'wiphy0':
                continue

            if resource in resource_data:
                matched_resources.add(resource)
                self.devices_data[port_id] = {'device type': None, 'cmd': None, 'ip': None}
                self.devices_data[port_id]['device type'] = resource_data[resource]['device type']
                self.devices_data[port_id]['ip'] = resource_data[resource]['ctrl-ip']
                # WiFi station's own address (distinct from ctrl-ip) -- clients must join
                # multicast on this or the OS picks Ethernet and receives nothing.
                self.devices_data[port_id]['sta_ip'] = port_data_dict.get('ip')
                self.devices_data[port_id]['hostname'] = resource_data[resource]['hostname'] if resource_data[resource]['device type'] != 'Android' else resource_data[resource]['user']
                self.devices_data[port_id]['rssi'] = port_data_dict['signal']
                self.devices_data[port_id]['channel'] = port_data_dict['channel']
                self.devices_data[port_id]['mac'] = port_data_dict['mac']
                self.devices_data[port_id]['link rate'] = port_data_dict['rx-rate']
                self.devices_data[port_id]['adb_id'] = None if resource_data[resource]['device type'] != 'Android' else resource_data[resource].get('adb_id')

        # A selected resource can still silently vanish here if its WiFi station
        # port failed the phantom/down/wiphy0 checks above -- report exactly why.
        for resource in resource_id:
            if resource in matched_resources:
                continue
            label = resource_data[resource].get('hostname') or resource_data[resource].get('user') or resource
            candidates = []
            for port_data_dict in ports:
                port_id = list(port_data_dict.keys())[0]
                parts = port_id.split('.')
                if len(parts) >= 2 and f"{parts[0]}.{parts[1]}" == resource:
                    pd = port_data_dict[port_id]
                    candidates.append(
                        f"{port_id}: phantom={pd.get('phantom')} down={pd.get('down')} "
                        f"parent_dev={pd.get('parent dev')!r}"
                    )
            if candidates:
                logger.warning(f"[PORTS] {resource} ({label}) was selected but every candidate port failed the "
                               f"phantom/down/wiphy0 check, so it's being dropped from this test:")
                for c in candidates:
                    logger.warning(f"  {c}")
            else:
                logger.warning(f"[PORTS] {resource} ({label}) was selected but /ports/all has no port entry "
                               f"for it at all -- it's being dropped from this test.")

        logger.info(self.devices_data)

    def filter_devices(self, resources_list):
        resource_data = {}
        for resource_data_dict in resources_list:
            resource_id = list(resource_data_dict.keys())[0]
            resource_data_dict = resource_data_dict[resource_id]

            devices = ['Linux/Interop', 'Windows', 'Mac OS', 'Android']
            if resource_data_dict['device type'] in devices and resource_data_dict.get('phantom') is False:
                resource_data[resource_id] = resource_data_dict

        # Sort devices so Android appears last
        sorted_resource_data = dict(
            sorted(
                resource_data.items(),
                key=lambda item: item[1]['device type'].lower() == "android"
            )
        )

        return sorted_resource_data

    def _json_get_retry(self, endpoint, attempts=3, delay=2):
        """GET a LANforge JSON endpoint, retrying on transient failures."""
        last_err = None
        for attempt in range(1, attempts + 1):
            try:
                return self.json_get(endpoint)
            except Exception as e:
                last_err = e
                logger.warning(f"json_get {endpoint} failed (attempt {attempt}/{attempts}): {e}")
                if attempt < attempts:
                    time.sleep(delay)
        raise RuntimeError(f"json_get {endpoint} failed after {attempts} attempts: {last_err}")

    def get_resource_data(self):
        # /adb/devices serializes "phantom" as a string, not the bool /resource/all uses,
        # so `x is False` would silently reject every entry -- normalize both before comparing.
        def _is_not_phantom(value):
            if isinstance(value, bool):
                return value is False
            return str(value).strip().lower() == "false"

        # Step 1: Get resource data
        resources_list = self._json_get_retry("/resource/all")["resources"]
        adb_device_list = self._json_get_retry("/adb/devices")["devices"]

        logger.info(f"\n[ADB] /adb/devices returned {len(adb_device_list)} entr{'y' if len(adb_device_list) == 1 else 'ies'}:")
        for adb_device in adb_device_list:
            _adb_id = list(adb_device.keys())[0]
            _v = adb_device[_adb_id]
            logger.info(f"  adb_id={_adb_id!r}  resource-id={_v.get('resource-id')!r}  phantom={_v.get('phantom')!r}")

        matched_resource_ids = set()
        for adb_device in adb_device_list:
            adb_id = list(adb_device.keys())[0]
            adb_values = adb_device[adb_id]
            # Normalize both sides -- guards against str/whitespace/type mismatches
            # between how /adb/devices and /resource/all represent the same id.
            resource_id = str(adb_values.get("resource-id", "")).strip()
            for resource_data_dict in resources_list:
                res_id = list(resource_data_dict.keys())[0]
                if str(res_id).strip() == resource_id and _is_not_phantom(adb_values.get("phantom")):
                    resource_data_dict[res_id]["adb_id"] = adb_id
                    matched_resource_ids.add(res_id)
                    break

        # Manual fallback: --adb_map lets an operator hand-map an Android resource to
        # its adb_id when the automatic match above misses it. Applied last, so it wins.
        if self.adb_map:
            for res_id, mapped_adb_id in self.adb_map.items():
                for resource_data_dict in resources_list:
                    if list(resource_data_dict.keys())[0] == res_id:
                        resource_data_dict[res_id]["adb_id"] = mapped_adb_id
                        matched_resource_ids.add(res_id)
                        logger.info(f"[ADB] Manually mapped {res_id} -> {mapped_adb_id} (--adb_map override)")
                        break

        # Flag Android resources the resource-id match missed -- not final, a
        # MAC-address fallback below may still resolve them once port data loads.
        for resource_data_dict in resources_list:
            res_id = list(resource_data_dict.keys())[0]
            info = resource_data_dict[res_id]
            if info.get("device type") == "Android" and res_id not in matched_resource_ids:
                logger.info(f"[ADB] {res_id} ({info.get('hostname') or info.get('user')}) didn't match by "
                            f"resource-id -- will retry by MAC address once port data loads.")

        resource_data = self.filter_devices(resources_list)

        headers = ["Index", "Resource ID", "Hostname", "IP", "Device Type"]
        rows = []
        resource_keys = list(resource_data.keys())

        for i, res_id in enumerate(resource_keys):
            res = resource_data[res_id]
            rows.append([
                i + 1,
                res_id,
                res.get("hostname", "N/A"),
                res.get("ctrl-ip", "N/A"),
                res.get("device type", "N/A"),
            ])

        logger.info("Available Devices:")
        logger.info(tabulate(rows, headers=headers, tablefmt="fancy_grid", disable_numparse=True))

        # Step 3: User selection
        selection = input("Select devices (example: 1,3,5): ")
        selected_indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
        selected_ids = [resource_keys[i] for i in selected_indices if 0 <= i < len(resource_keys)]
        self.selected_devices_ordered = selected_ids
        selected_resources = {res_id: resource_data[res_id] for res_id in selected_ids}
        logger.info(f"\n Selected Devices:\n{selected_resources}")

        # Step 4: Proceed with port collection
        self.get_port_data(selected_resources)

        # Fallback: match remaining Android devices by MAC address instead of
        # resource-id, since both /adb/devices and get_port_data expose it -- no
        # manual --adb_map needed for these devices.
        mac_keys = ("mac", "mac address", "wifi mac", "sta mac", "station mac")

        def _extract_mac(values):
            for key in mac_keys:
                val = values.get(key)
                if val:
                    return str(val).strip().lower()
            return None

        for port_id, info in self.devices_data.items():
            if info.get("device type") != "Android" or info.get("adb_id"):
                continue  # not Android, or already matched above
            port_mac = str(info.get("mac", "")).strip().lower()
            if not port_mac:
                continue
            for adb_device in adb_device_list:
                adb_id = list(adb_device.keys())[0]
                adb_values = adb_device[adb_id]
                if not _is_not_phantom(adb_values.get("phantom")):
                    continue
                if _extract_mac(adb_values) == port_mac:
                    info["adb_id"] = adb_id
                    logger.info(f"[ADB] Matched {port_id} -> {adb_id} by MAC address ({port_mac})")
                    break
            else:
                logger.warning(f"[ADB] {port_id}: still no adb_id after the MAC fallback. "
                               f"Raw /adb/devices field names seen: "
                               f"{[list(d[list(d.keys())[0]].keys()) for d in adb_device_list[:1]]}")

        # Select one device as host
        device_ids = list(self.devices_data.keys())
        host_id = None

        def is_android(device_id):
            return self.devices_data[device_id]['device type'].lower() == "android"

        if self.external_source:
            # External source: no device from this pool is ever selected as host,
            # regardless of --host_res/--video_name -- every device runs as a client.
            host_id = None
            self.host_res = None
            logger.info("External multicast source mode (--external_source): all selected "
                        "devices will run as clients; no clustered resource laptop will be "
                        "used as the VLC host.")
        else:
            while True:
                if self.host_res:
                    for dev_id in device_ids:
                        if dev_id.startswith(self.host_res + '.'):
                            if is_android(dev_id):
                                logger.warning("Android device cannot be selected as HOST.")
                                self.host_res = None
                                break
                            host_id = dev_id
                            self.host_res = host_id
                            break

                elif self.video_name:
                    # Default host is first NON-Android device
                    non_android_hosts = [d for d in device_ids if not is_android(d)]

                    if not non_android_hosts:
                        logger.error("No valid non-Android devices available to act as host.")
                        sys.exit(1)

                    host_id = non_android_hosts[0]
                    self.host_res = host_id
                    logger.info(f"Using first non-Android device as host: {host_id}")

                else:
                    logger.info("No host specified and no video stream — all devices are clients")
                    break

                if host_id:
                    break

                # Prompt reselection
                logger.info("\nAvailable NON-Android devices:")
                for idx, dev_id in enumerate(device_ids):
                    if not is_android(dev_id):
                        info = self.devices_data[dev_id]
                        logger.info(f"{idx}: {dev_id} ({info['device type']})")

                try:
                    idx = int(input("Select a NON-Android device index to use as host: "))
                    candidate = device_ids[idx]
                    if is_android(candidate):
                        logger.warning("Android device cannot be host. Try again.")
                    else:
                        host_id = candidate
                        self.host_res = host_id
                except Exception:
                    logger.warning("Invalid selection. Try again.")

        # Step 5: Assign vlc streaming command by OS
        if self.devices_data:
            for device in self.devices_data:
                info = self.devices_data[device]
                os_type = info['device type'].lower()
                is_host = device == host_id
                if is_host:
                    if "linux" in os_type:
                        cmd = (
                            f'su -l lanforge ctvlc.bash {device.split(".")[2]} host "{self.video_name}" {self.mcast_addr} {self.mcast_port} {self.duration} {device} {self.fserver}:{self.fport}'
                        )
                    elif "windows" in os_type:
                        cmd = (
                            f'py ctvlc.py host --media "{self.video_name}" '
                            f'--mcast_ip "{self.mcast_addr}" --port {self.mcast_port} --duration {self.duration} --fserver {self.fserver}:{self.fport} --client_id {device}'
                        )
                    elif "mac" in os_type:
                        cmd = (
                            f'bash ctvlc.bash {device.split(".")[2]} host "{self.video_name}" "{self.mcast_addr}" {self.mcast_port} {self.duration} {device} {self.fserver}:{self.fport}'
                        )
                    elif "android" in os_type:
                        adb_id = info.get("adb_id")
                        if not adb_id:
                            logger.warning(f"No adb_id found for Android device {device}. Skipping command assignment.")
                            continue
                        cmd = (
                            f'python3 vlc_android.py --serial {adb_id.split(".")[-1]} --'
                            f'adb -s {adb_id} shell am start -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity '
                            f'-e vlc_args "--intf=rc --extraintf=rc --rc-host=localhost:{self.fport} --loop '
                            f'--sout=#duplicate{{dst=display,dst=std{{access=udp,mux=ts,dst={self.mcast_addr}:{self.mcast_port}}}}} --input-repeat=9999" '
                            f'-e input "{self.video_name}"'
                        )
                else:  # Client vlc udp://@239.255.0.1:1234 -vvv
                    # Optional additional streams + switch config (laptop
                    # clients only -- see the ctvlc.py/ctvlc.bash multi-stream support).
                    dual_bash_args = ""
                    dual_win_args = ""
                    # In host-rotation mode content changes at the source on one group,
                    # so clients must stay on that URL -- a playlist would fight the rotation.
                    if self.extra_streams and not self.host_rotate:
                        extra_streams_str = ",".join(f"{ip}:{port}" for ip, port in self.extra_streams)
                        dual_bash_args = f' "{extra_streams_str}" {self.switch_mode} {self.switch_value}'
                        switch_flag = (
                            f'--switch_every {self.switch_value}' if self.switch_mode == "iteration"
                            else f'--switch_interval {self.switch_value}'
                        )
                        dual_win_args = f' --extra_streams "{extra_streams_str}" --switch_mode {self.switch_mode} {switch_flag}'

                    # Join multicast on the WiFi station, not whichever
                    # interface the OS would pick (usually wired Ethernet).
                    prefix = f"{self.client_script_dir}/" if self.client_script_dir else ""
                    simple_bash = " simple" if self.client_simple else ""
                    simple_win = " --simple" if self.client_simple else ""
                    sta_ip = info.get("sta_ip")
                    miface_arg = f' --miface_addr {sta_ip}' if sta_ip else ''
                    if not sta_ip:
                        logger.warning(f"{device}: no station IP known, so the client will let the OS "
                                       f"choose its multicast interface. If it has both Ethernet and WiFi it "
                                       f"may join on Ethernet and receive nothing.")

                    if "linux" in os_type:
                        cmd = (
                            f'su -l lanforge {prefix}ctvlc.bash {device.split(".")[2]} client - {self.mcast_addr} {self.mcast_port} '
                            f'{self.duration} {device} {self.fserver}:{self.fport}{dual_bash_args}'
                        )
                    elif "windows" in os_type:
                        cmd = (
                            f'py -u {prefix}ctvlc.py client '
                            f'--mcast_ip {self.mcast_addr} --port {self.mcast_port} --duration {self.duration} --fserver {self.fserver}:{self.fport} '
                            f'--client_id {device}{miface_arg}{dual_win_args}{simple_win}'
                        )
                    elif "mac" in os_type:
                        # mac's ctvlc.bash always expects 3 positional extra-stream slots,
                        # unlike linux -- fall back to empty placeholders when unset.
                        mac_dual_args = dual_bash_args or ' "" "" ""'
                        cmd = (
                            f'bash {prefix}ctvlc.bash {device.split(".")[2]} client - {self.mcast_addr} {self.mcast_port} '
                            f'{self.duration} {device} {self.fserver}:{self.fport}{mac_dual_args} ""{simple_bash}'
                        )
                    elif "android" in os_type:
                        adb_id = info.get("adb_id")
                        if not adb_id:
                            logger.warning(f"No adb_id found for Android device {device}. Skipping command assignment.")
                            continue
                        cmd = (
                            f'python3 {self.android_script} --serial {adb_id.split(".")[-1]} --mcast_ip {self.mcast_addr} --port {self.mcast_port} '
                            f'--duration {self.duration} --fserver {self.manager_ip}:{self.fport} --client_id {device}'
                            + (' --simple' if self.android_simple else '')
                            + (' --no_stats' if self.android_no_stats else '')
                        )
                logger.info(self.devices_data[device])
                self.devices_data[device]['cmd'] = cmd
        else:
            logger.warning("No compatible devices found.")

        logger.info("\nFinal Device Commands for vlc streaming:")
        for device, info in self.devices_data.items():
            logger.info(f"{device} → {info['ip']} ({info['device type']}): {info['cmd']}")

    def all_stream_targets(self):
        """Every configured stream as (ip, port), primary first."""
        return [(self.mcast_addr, self.mcast_port)] + list(self.extra_streams)

    @staticmethod
    def multicast_has_traffic(mcast_ip, port, iface_ip=None, seconds=3):
        """Join a multicast group as a real receiver and report whether data arrives.
        Needs no root (unlike tcpdump) and proves the stream is actually on the network."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", int(port)))
            mreq = struct.pack("4s4s", socket.inet_aton(mcast_ip),
                               socket.inet_aton(iface_ip or "0.0.0.0"))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.settimeout(1.0)
            total = 0
            end = time.time() + seconds
            while time.time() < end:
                try:
                    data, _ = sock.recvfrom(65535)
                    total += len(data)
                except socket.timeout:
                    continue
            return total
        except Exception as e:
            logger.warning(f"[HOST] Could not check {mcast_ip}:{port} -- {e}")
            return 0
        finally:
            sock.close()

    def start_local_hosts(self):
        """Launch one local VLC per configured stream on this machine. Media files map in
        order onto the streams: first file to --mcast_addr/--mcast_port, rest to --extra_streams."""
        if not self.host_media:
            return

        targets = self.all_stream_targets()
        if len(self.host_media) > len(targets):
            logger.error(f"{len(self.host_media)} media files given but only {len(targets)} "
                         f"stream(s) configured. Add more via --extra_streams, or pass fewer files.")
            sys.exit(1)

        logger.info("\n[HOST] Pre-cleanup: killing any old VLC processes on this machine...")
        subprocess.run(["pkill", "-9", "vlc"], capture_output=True)
        time.sleep(1)

        env = dict(os.environ)
        if self.host_gui:
            # VLC's Qt interface needs a display; :1 is what ctvlc.bash has
            # always used on LANforge.
            env.setdefault("DISPLAY", ":1")

        # Hosts must outlive the client run, or clients lose the stream
        # partway through.
        host_duration = self.duration + 120

        for idx, media in enumerate(self.host_media):
            if not os.path.isfile(media):
                logger.error(f"Media file not found: {media}")
                self.stop_local_hosts()
                sys.exit(1)

            ip, port = targets[idx]
            logger.info(f"[HOST] Stream {idx + 1}: {media} -> {ip}:{port}")

            # One host per interface, so a single run can serve client
            # networks that no single interface reaches.
            ifaces = self.host_ifaces or [None]
            for j, iface in enumerate(ifaces):
                cmd = [
                    sys.executable, "ctvlc.py", "host",
                    "--media", media,
                    "--mcast_ip", str(ip),
                    "--port", str(port),
                    # Every host needs its own RC port, or a later ctvlc.py
                    # would connect to an earlier VLC's socket instead of its own.
                    "--rc_port", str(4212 + (idx * len(ifaces)) + j),
                    "--duration", str(host_duration),
                    "--client_id", f"wan_host{idx + 1}",
                ]
                if iface:
                    cmd += ["--miface", iface]
                    logger.info(f"[HOST]   out {iface}")
                if not self.host_gui:
                    cmd.append("--headless")
                if self.host_vb:
                    cmd += ["--vb", str(self.host_vb)]

                # Hosts deliberately do NOT report stats to the collector:
                # they aren't devices under test, and their POSTs are noise.
                proc = subprocess.Popen(cmd, env=env,
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                self.host_procs.append(proc)

        logger.info("[HOST] Waiting for streams to come up...")
        time.sleep(8)

        all_ok = True
        if all(p.poll() is not None for p in self.host_procs):
            logger.error("[HOST] Every host process exited immediately. "
                         "Is VLC installed on this machine? Try: which vlc")
            all_ok = False

        for _idx, (ip, port) in enumerate(targets[:len(self.host_media)]):
            for iface in (self.host_ifaces or [None]):
                iface_ip = self.local_ip_for_iface(iface) if iface else None
                label = f"{ip}:{port}" + (f" via {iface}" if iface else "")
                total = self.multicast_has_traffic(ip, port, iface_ip)
                if total:
                    logger.info(f"[HOST] {label} is transmitting ({total/1024:.0f} KiB sampled)")
                else:
                    logger.warning(f"[HOST] {label} -- no traffic detected. Clients on that "
                                   f"network will receive nothing.")
                    all_ok = False

        if not all_ok:
            logger.warning("[HOST] One or more streams are not transmitting -- continuing anyway, "
                           "but expect clients to report zero bytes.")

    @staticmethod
    def local_ip_for_iface(iface):
        """Best-effort local IPv4 for an interface name, for the join check."""
        try:
            out = subprocess.run(["ip", "-4", "-o", "addr", "show", iface],
                                 capture_output=True, text=True).stdout
            for part in out.split():
                if "/" in part and part.count(".") == 3:
                    return part.split("/")[0]
        except Exception:
            pass
        return None

    def _launch_one_host(self, media, ip, port, rc_port, duration, iface=None):
        """Launch a single VLC host process and return it."""
        env = dict(os.environ)
        if self.host_gui:
            env.setdefault("DISPLAY", ":1")

        cmd = [
            sys.executable, "ctvlc.py", "host",
            "--media", media,
            "--mcast_ip", str(ip),
            "--port", str(port),
            "--rc_port", str(rc_port),
            "--duration", str(duration),
            "--client_id", "wan_host_rotate",
        ]
        if iface:
            cmd += ["--miface", iface]
        if not self.host_gui:
            cmd.append("--headless")
        if self.host_vb:
            cmd += ["--vb", str(self.host_vb)]

        return subprocess.Popen(cmd, env=env,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

    def _launch_on_all_ifaces(self, media, ip, port, duration):
        """Launch one VLC host per configured interface. Each needs its own RC port so a
        later ctvlc.py cannot connect to an earlier VLC's socket."""
        ifaces = self.host_ifaces or [None]
        procs = []
        for i, iface in enumerate(ifaces):
            procs.append(self._launch_one_host(media, ip, port, 4212 + i, duration, iface=iface))
            if iface:
                logger.info(f"[HOST]   out {iface} (rc_port {4212 + i})")
        return procs

    def _rotation_loop(self, ip, port, host_duration):
        """Cycle through the media files on one multicast group, recording each switch
        as a transition so it lands in the report."""
        interval = self.switch_value if self.switch_mode == "time" else max(self.switch_value * 3, 10)
        if self.switch_mode == "iteration":
            logger.info(f"[ROTATE] switch_mode=iteration -> switching every ~{interval}s "
                        f"({self.switch_value} poll cycles at ~3s each)")

        while not self.rotate_stop.is_set():
            # Wait out this stream's turn, checking often so shutdown is prompt.
            if self.rotate_stop.wait(timeout=interval):
                break

            from_idx = self.current_media_idx
            to_idx = (from_idx + 1) % len(self.host_media)

            logger.info(f"[ROTATE] Switching source: {os.path.basename(self.host_media[from_idx])} "
                        f"-> {os.path.basename(self.host_media[to_idx])} on {ip}:{port}")

            # Stop the current source before starting the next, so only one
            # thing is ever transmitting on this group.
            for proc in self.host_procs:
                try:
                    proc.terminate()
                except Exception:
                    pass
            time.sleep(1)
            subprocess.run(["pkill", "-9", "vlc"], capture_output=True)
            time.sleep(1)

            self.host_procs = self._launch_on_all_ifaces(
                self.host_media[to_idx], ip, port, host_duration)
            self.current_media_idx = to_idx

            # Record it for the report. The orchestrator knows exactly when it
            # switched, so these timestamps are authoritative.
            self.transitions.setdefault("host_rotation", []).append({
                "transition": True,
                "switch_time": time.time(),
                "switch_mode": self.switch_mode,
                "from_stream": from_idx + 1,
                "to_stream": to_idx + 1,
                "from_url": os.path.basename(self.host_media[from_idx]),
                "to_url": os.path.basename(self.host_media[to_idx]),
                "confirmed_playing": f"{ip}:{port}",
                "pre_switch_stats": {},
            })

    def start_host_rotation(self):
        """Host-side rotation: one multicast group, media files played in turn. Every
        client (laptop and Android) stays on the same URL and just sees the content change."""
        ip, port = self.mcast_addr, self.mcast_port
        host_duration = self.duration + 120

        logger.info("\n[ROTATE] Host-side stream rotation")
        logger.info(f"[ROTATE] Group: {ip}:{port}   Media: "
                    f"{', '.join(os.path.basename(m) for m in self.host_media)}")
        logger.info(f"[ROTATE] Switching every {self.switch_value}"
                    f"{'s' if self.switch_mode == 'time' else ' poll cycles'}")

        logger.info("[HOST] Pre-cleanup: killing any old VLC processes on this machine...")
        subprocess.run(["pkill", "-9", "vlc"], capture_output=True)
        time.sleep(1)

        for media in self.host_media:
            if not os.path.isfile(media):
                logger.error(f"Media file not found: {media}")
                sys.exit(1)

        self.host_procs = self._launch_on_all_ifaces(
            self.host_media[0], ip, port, host_duration)
        self.current_media_idx = 0

        logger.info("[HOST] Waiting for the first stream to come up...")
        time.sleep(8)

        for iface in (self.host_ifaces or [None]):
            iface_ip = self.local_ip_for_iface(iface) if iface else None
            total = self.multicast_has_traffic(ip, port, iface_ip)
            label = f"{ip}:{port}" + (f" via {iface}" if iface else "")
            if total:
                logger.info(f"[HOST] {label} is transmitting ({total/1024:.0f} KiB sampled)")
            else:
                logger.warning(f"[HOST] {label} -- no traffic detected. Check that this "
                               f"interface is on the network your clients are on.")

        self.rotate_stop.clear()
        self.rotate_thread = threading.Thread(
            target=self._rotation_loop, args=(ip, port, host_duration), daemon=True)
        self.rotate_thread.start()

    def stop_local_hosts(self):
        """Stop any VLC hosts this script started."""
        self.rotate_stop.set()
        if self.rotate_thread and self.rotate_thread.is_alive():
            self.rotate_thread.join(timeout=5)
        if not self.host_procs:
            return
        logger.info("[HOST] Stopping local streams...")
        for proc in self.host_procs:
            try:
                proc.terminate()
            except Exception:
                pass
        time.sleep(2)
        subprocess.run(["pkill", "-9", "vlc"], capture_output=True)
        self.host_procs = []

    def start_generic(self):
        self.generic_endps_profile.start_cx()
        self.start_time = datetime.now()

    def stop_generic(self):
        self.generic_endps_profile.stop_cx()
        self.stop_time = datetime.now()

    def create_android(self, lanforge_res, ports=None, sleep_time=.5, debug_=False, suppress_related_commands_=None, real_client_os_types=None):
        if ports and real_client_os_types and len(real_client_os_types) == 0:
            logger.error('Real client operating systems types is empty list')
            raise ValueError('Real client operating systems types is empty list')
        created_cx = []
        created_endp = []

        if not ports:
            ports = []

        if self.debug:
            debug_ = True

        post_data = []
        endp_tpls = []
        for port_name in ports:
            port_info = self.name_to_eid(port_name)
            resource = port_info[1]
            shelf = port_info[0]
            if real_client_os_types:
                name = port_name
            else:
                name = port_info[2]

            gen_name_a = "%s-%s" % ('vlc', '_'.join(port_name.split('.')))
            endp_tpls.append((shelf, resource, name, gen_name_a))

        logger.info(f"endp_tpls {endp_tpls}")
        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            if real_client_os_types:
                name = endp_tpl[2].split('.')[2]
            else:
                name = endp_tpl[2]
            gen_name_a = endp_tpl[3]

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": lanforge_res,
                "port": 'eth0',
                "type": "gen_generic"
            }
            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        if sleep_time:
            time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            gen_name_a = endp_tpl[3]
            self.generic_endps_profile.set_flags(gen_name_a, "ClearPortOnStart", 1)

        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            cx_name = "CX_%s-%s" % ("generic", gen_name_a)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a
            }
            post_data.append(data)
            created_cx.append(cx_name)
            created_endp.append(gen_name_a)

        for data in post_data:
            url = "/cli-json/add_cx"
            self.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
        if sleep_time:
            time.sleep(sleep_time)

        for data in post_data:
            self.json_post("/cli-json/show_cx", {
                "test_mgr": "default_tm",
                "cross_connect": data["alias"]
            })
        return True, created_cx, created_endp

    def expected_endpoint_names(self):
        """
        The endpoint/CX names this run will create, derived from the same
        naming rules create() and create_android() use.
        """
        pairs = []
        for eid, device in self.devices_data.items():
            if device.get("device type", "").lower() == "android":
                # create_android(): endpoint "vlc-1_45_wlan0",
                # cross-connect "CX_generic-vlc-1_45_wlan0".
                endp = "vlc-%s" % "_".join(eid.split("."))
                cx = f"CX_generic-{endp}"
            else:
                # Laptops: endpoint "generic-1.50.en0",
                # cross-connect "CX_generic-1.50.en0" -- note the "generic-"
                # prefix is NOT doubled.
                endp = f"generic-{eid}"
                cx = f"CX_generic-{eid}"
            pairs.append((cx, endp))
        return pairs

    def remove_stale_endpoints(self):
        """Delete cross-connects/endpoints this run is about to create, if a previous run
        left them behind -- LANforge won't let a leftover CX be reassigned a new command."""
        logger.info("[CLEANUP] Removing stale generic cross-connects from previous runs...")

        pairs = self.expected_endpoint_names()
        if not pairs:
            logger.info("[CLEANUP] No devices selected yet -- nothing to clean.")
            return

        for cx_name, _ in pairs:
            try:
                self.json_post("cli-json/rm_cx",
                               {"test_mgr": "default_tm", "cx_name": cx_name})
            except Exception as e:
                logger.warning(f"[CLEANUP] rm_cx {cx_name}: {e}")

        # LANforge needs a moment to release endpoints from a removed CX.
        time.sleep(3)

        for _, endp_name in pairs:
            try:
                self.json_post("cli-json/rm_endp", {"endp_name": endp_name})
            except Exception as e:
                logger.warning(f"[CLEANUP] rm_endp {endp_name}: {e}")

        time.sleep(2)

        # Confirm they're actually gone -- a surviving CX silently pins the device to
        # its original command, which is exactly the failure this cleanup prevents.
        survivors = []
        for cx_name, _ in pairs:
            try:
                still_there = self.json_get(f"/cx/{cx_name}")
            except Exception:
                still_there = None
            if still_there and isinstance(still_there, dict):
                body = str(still_there).lower()
                if cx_name.lower() in body and "not found" not in body:
                    survivors.append(cx_name)

        if survivors:
            logger.warning("[CLEANUP] These cross-connects could NOT be removed:")
            for cx_name in survivors:
                logger.warning(f"    {cx_name}")
            logger.warning("    Those devices will keep running the command from the run that first")
            logger.warning("    created the CX -- new options will NOT take effect. Delete them by hand")
            logger.warning("    in the LANforge GUI (Generic tab), or stop the test manager, then re-run.")
        else:
            logger.info(f"[CLEANUP] Cleared {len(pairs)} cross-connect/endpoint pair(s).")

        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []

    def create(self):
        device_types = [device['device type'] for device in self.devices_data.values()]
        logger.info(device_types)
        for device_id, device in self.devices_data.items():
            if not device.get("cmd"):
                # No command was built for this device (usually a missing Android adb_id,
                # see get_resource_data) -- skip it rather than crash the whole run.
                logger.warning(f"[SKIP] {device_id}: no command was generated for this device "
                               f"(device type={device.get('device type')}, adb_id={device.get('adb_id')}). "
                               f"Not creating a generic endpoint for it.")
                continue
            try:
                if device['device type'].lower() == "android":
                    if not device.get("adb_id"):
                        logger.warning(f"[SKIP] {device_id}: Android device has no adb_id, cannot create its endpoint.")
                        continue
                    status, created_cx, created_endp = self.create_android(lanforge_res=device["adb_id"].split(".")[1], ports=[device_id], real_client_os_types=['Linux'])
                    logger.info(f"return from android create {status} {created_cx} {created_endp}")
                    self.generic_endps_profile.created_endp.extend(created_endp)
                    self.generic_endps_profile.created_cx.extend(created_cx)
                    self.generic_endps_profile.set_cmd(created_endp[0], cmd=device["cmd"])
                else:
                    new_cx_index = len(self.generic_endps_profile.created_cx)
                    self.generic_endps_profile.create(ports=[device_id], real_client_os_types=device["device type"])
                    self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[new_cx_index], cmd=device["cmd"])
            except Exception as e:
                # One device's endpoint/CX creation failing (e.g. a transient LANforge
                # API error) shouldn't stop every other device from being set up.
                logger.error(f"[SKIP] {device_id}: failed to create generic endpoint: {e}")

        logger.info(self.generic_endps_profile.created_endp)

    def cleanup(self):
        self.generic_endps_profile.cleanup()
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []

    def start_flask_server(self):

        @self.app.route('/stats', methods=['POST'])
        def upload_stats():
            temp_data = request.get_json()
            for client_id, stats in temp_data.items():
                if isinstance(stats, dict) and stats.get("transition"):
                    # Stream-switch event -- keep every one of these (not just
                    # the latest), so the report can list each transition.
                    self.transitions.setdefault(client_id, []).append(stats)
                elif isinstance(stats, dict) and stats.get("automation_failed"):
                    self.android_errors[client_id] = stats.get("error", "unknown error")
                    logger.error(f"[ANDROID] {client_id}: {self.android_errors[client_id]}")
                else:
                    self.stats[client_id] = stats
            logger.info(f"[STATS] received from {', '.join(temp_data.keys())} "
                        f"({len(self.stats)} client(s) reporting)")
            return jsonify({"status": "success"}), 200

        # New route to check the health of the Flask server
        @self.app.route('/check_health', methods=['GET'])
        def check_health():
            # Include our PID so wait_for_flask can tell OUR server apart from
            # an orphaned earlier run that is also listening on this port.
            return jsonify({"status": "healthy", "pid": os.getpid()}), 200

        @self.app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        try:
            # werkzeug's per-request logging would print a line for every ~3s stats
            # POST, burying the interactive device-selection prompt -- keep it quiet.
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            self.app.run(host='0.0.0.0', port=5959, debug=False, threaded=True, use_reloader=False)

        except Exception as e:
            logger.error(f"Error starting Flask server: {e}")
            sys.exit(0)

    def preflight_checks(self):
        """Fail fast, loudly, and with a fix -- before launching anything. Every one of
        these has silently produced a "ran but collected nothing" result at least once."""
        problems = []

        # 1. Stats port already taken? An orphaned run from a crash would still
        #    answer /check_health, so this run's clients report to it instead.
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("0.0.0.0", 5959))
        except OSError:
            problems.append(
                "Port 5959 is already in use -- most likely an orphaned "
                "lf_interop_vlc.py from an earlier run. It will answer the health "
                "check and swallow every client's stats, so this run would collect "
                "nothing.\n"
                "      Fix:  pkill -f lf_interop_vlc.py     (then re-run)\n"
                "      Check: sudo lsof -i :5959"
            )
        finally:
            probe.close()

        # 2. Scripts the clients will be told to run must exist.
        if not os.path.isfile("ctvlc.py"):
            problems.append(
                f"ctvlc.py not found in {os.getcwd()} -- laptop clients are launched with a "
                f"relative path, so it must sit beside this script."
            )

        if not os.path.isfile(self.android_script):
            problems.append(
                f"vlc_android.py not found at {self.android_script}. Set --android_script to "
                f"its real location on the machine with the phones attached."
            )
        else:
            # Catch a stale copy directly: current vlc_android.py makes uiautomator2
            # optional, so a missing marker means phones will hit ModuleNotFoundError.
            try:
                with open(self.android_script) as fh:
                    body = fh.read()
                if "U2_AVAILABLE" not in body:
                    problems.append(
                        f"{self.android_script} is an OLD version (no optional-uiautomator2 "
                        f"support). Android will fail with "
                        f"ModuleNotFoundError: No module named 'uiautomator2'.\n"
                        f"      Fix: deploy the current vlc_android.py to that path.\n"
                        f"      Find other copies: find / -name vlc_android.py 2>/dev/null"
                    )
            except Exception as e:
                logger.warning(f"[PREFLIGHT] Could not inspect {self.android_script}: {e}")

        # 3. Local hosting prerequisites.
        if self.host_media:
            for media in self.host_media:
                if not os.path.isfile(media):
                    problems.append(f"Media file not found: {media}")

            from shutil import which
            if which("vlc") is None:
                problems.append(
                    "VLC is not installed on this machine, so --host_media cannot "
                    "serve anything. Check with: which vlc"
                )

            if not self.host_ifaces:
                logger.warning("[PREFLIGHT] --host_media given without --host_iface. The OS "
                               "routing table will pick the outbound interface, which may not be "
                               "the network your clients are on.")

            targets = self.all_stream_targets()
            if not self.host_rotate and len(self.host_media) > len(targets):
                problems.append(
                    f"{len(self.host_media)} media files but only {len(targets)} stream(s) "
                    f"configured. Add --extra_streams, or use --host_rotate to play them "
                    f"in turn on one group."
                )

        if problems:
            logger.error("\n" + "=" * 70)
            logger.error("PREFLIGHT FAILED -- fix these before running:")
            logger.error("=" * 70)
            for i, p in enumerate(problems, 1):
                logger.error(f"  {i}. {p}")
            logger.error("=" * 70 + "\n")
            sys.exit(1)

        logger.info("[PREFLIGHT] OK")

    def run_flask_server(self):
        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        self.wait_for_flask()

    def wait_for_flask(self, url="http://127.0.0.1:5959/check_health", timeout=10):
        """Wait until the Flask server is up, but exit if it takes longer than `timeout` seconds."""
        start_time = time.time()  # Record the start time
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    served_by = None
                    try:
                        served_by = response.json().get("pid")
                    except Exception:
                        pass
                    if served_by is not None and served_by != os.getpid():
                        logger.error(
                            f" Port 5959 is answering, but from PID {served_by}, not this "
                            f"process ({os.getpid()}). An orphaned lf_interop_vlc.py is "
                            f"holding the port and would receive all client stats. "
                            f"Run: pkill -f lf_interop_vlc.py")
                        sys.exit(1)
                    logger.info("✅ Flask server is up and running!")
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        logger.error(" Flask server did not start within 10 seconds. Exiting.")
        sys.exit(1)

    def generate_test_setup_info(self):
        """Build the test-setup-info dict shown in the report's Input Parameters table."""
        mac = 0
        linux = 0
        win = 0
        android = 0
        device_list = []
        for devices in self.devices_data.values():
            if devices['device type'].lower() == "linux/interop":
                linux += 1
            elif devices['device type'].lower() == "windows":
                win += 1
            elif devices['device type'].lower() == "mac os":
                mac += 1
            elif devices['device type'].lower() == "android":
                android += 1
            device_list.append(devices["hostname"])

        test_setup_info = {
            'Test name': "VLC Streaming Test",
            'Devies': device_list,
            'No of Devices': f'Total ({mac+linux+win+android}) Windows({win}),Linux({linux}),Mac({mac}),Android({android})',
            "Test Duration (min)": self.duration/60,
            "Host ID": ("External source (no clustered host)" if self.external_source else self.host_res),
            "Test Type": "Video+Audio",
            "Multicast Port": self.mcast_port,
            "Multicast Address": self.mcast_addr
        }
        if self.extra_streams:
            total_streams = 1 + len(self.extra_streams)
            test_setup_info["Total Streams"] = total_streams
            test_setup_info["Additional Streams"] = ", ".join(
                f"{ip}:{port}" for ip, port in self.extra_streams
            )
            test_setup_info["Switch Mode"] = self.switch_mode
            test_setup_info["Switch Value"] = (
                f"{self.switch_value}s" if self.switch_mode == "time" else f"{self.switch_value} polls"
            )
        return test_setup_info

    def extract_data_for_reporting_for_laptop_clients(self):

        hostname, device_type, mac, channel, rssi, link = [], [], [], [], [], []
        video_decoded,  frames_displayed, frames_lost = [], [], []
        audio_decoded = []
        active_stream = []

        for eid, device in self.devices_data.items():
            if self.host_res and self.host_res == eid:
                # skipping host
                continue
            if device['device type'].lower() == "android":
                continue
            hostname.append(device.get("hostname", ""))
            device_type.append(device.get("device type", ""))
            mac.append(device.get("mac", ""))
            channel.append(device.get("channel", ""))
            rssi.append(device.get("rssi", ""))
            link.append(device.get("link rate", ""))

            stats = self.stats.get(eid)
            if stats:
                video_decoded.append(stats.get("video_decoded", "0"))
                audio_decoded.append(stats.get("audio_decoded", "0"))
                frames_displayed.append(stats.get("frames_displayed", "0"))
                frames_lost.append(stats.get("frames_lost", "0"))
                active_stream.append(stats.get("active_stream", "-"))
            else:
                video_decoded.append("0")
                audio_decoded.append("0")
                frames_displayed.append("0")
                frames_lost.append("0")
                active_stream.append("-")
        return {
            "hostnames": hostname,
            "device_types": device_type,
            "mac": mac,
            "channel": channel,
            "rssi": rssi,
            "link": link,
            "video_decoded": video_decoded,
            "frames_displayed": frames_displayed,
            "frames_lost": frames_lost,
            "audio_decoded": audio_decoded,
            "active_stream": active_stream
        }

    def extract_data_for_reporting_for_android_clients(self):
        hostname, device_type, mac, channel, rssi, link = [], [], [], [], [], []
        video_codec, audio_codec, audio_channels, audio_sample_rate = [], [], [], []
        demux_bitrate, input_bitrate = [], []
        framerate, buffering_events = [], []
        vlc_foreground = []
        for eid, device in self.devices_data.items():
            if device['device type'].lower() != "android":
                # skipping non-android clients
                continue
            hostname.append(device.get("hostname", ""))
            device_type.append(device.get("device type", ""))
            mac.append(device.get("mac", ""))
            channel.append(device.get("channel", ""))
            rssi.append(device.get("rssi", ""))
            link.append(device.get("link rate", ""))

            stats = self.stats.get(eid)
            # stats["parsed"] holds demux_bitrate_kbps, input_bitrate_kbps, video_codec,
            # audio_codec, channels, sample_rate_hz, framerate_fps, elapsed_time_sec (see vlc_android.py).
            stats = stats.get("parsed") if stats else None
            if stats:
                video_codec.append(stats.get("video_codec", "N/A"))
                audio_codec.append(stats.get("audio_codec", "N/A"))
                audio_channels.append(stats.get("channels", "N/A"))
                audio_sample_rate.append(stats.get("sample_rate_hz", "N/A"))
                demux_bitrate.append(stats.get("demux_bitrate_kbps", "0"))
                input_bitrate.append(stats.get("input_bitrate_kbps", "0"))
                framerate.append(stats.get("framerate_fps", "N/A"))
                buffering_events.append(stats.get("stall_events_so_far", "N/A"))
                fg = stats.get("vlc_in_foreground")
                vlc_foreground.append("Yes" if fg is True else ("No" if fg is False else "N/A"))
            else:
                video_codec.append("N/A")
                audio_codec.append("N/A")
                audio_channels.append("N/A")
                audio_sample_rate.append("N/A")
                demux_bitrate.append("0")
                input_bitrate.append("0")
                framerate.append("N/A")
                buffering_events.append("N/A")
                vlc_foreground.append("N/A")
        return {
            "hostnames": hostname,
            "device_types": device_type,
            "mac": mac,
            "channel": channel,
            "rssi": rssi,
            "link": link,
            "video_codec": video_codec,
            "audio_codec": audio_codec,
            "audio_channels": audio_channels,
            "audio_sample_rate": audio_sample_rate,
            "demux_bitrate": demux_bitrate,
            "input_bitrate": input_bitrate,
            "framerate": framerate,
            "buffering_events": buffering_events,
            "vlc_foreground": vlc_foreground
        }

    def extract_data_for_reporting_for_host(self):
        hostname, device_type, mac, channel, rssi, link = [], [], [], [], [], []
        input_bytes_read = []
        input_bitrate = []
        demux_bytes_read = []
        demux_bitrate = []
        discontinuities = []

        for eid, device in self.devices_data.items():
            if eid != self.host_res:
                # skipping client that is not host
                continue
            hostname.append(device.get("hostname", ""))
            device_type.append(device.get("device type", ""))
            mac.append(device.get("mac", ""))
            channel.append(device.get("channel", ""))
            rssi.append(device.get("rssi", ""))
            link.append(device.get("link rate", ""))

            stats = self.stats.get(eid)

            if stats:
                input_bytes_read.append(stats.get("input_bytes_read", "0 KiB"))

                input_bitrate.append(stats.get("input_bitrate", "0 kb/s"))

                demux_bytes_read.append(stats.get("demux_bytes_read", "0 KiB"))

                demux_bitrate.append(stats.get("demux_bitrate", "0 kb/s"))

                discontinuities.append(stats.get("discontinuities", "Constant"))
            else:
                input_bytes_read.append("0 KiB")
                input_bitrate.append("0 kb/s")
                demux_bytes_read.append("0 KiB")
                demux_bitrate.append("0 kb/s")
                discontinuities.append("0")

        return {
            "hostnames": hostname,
            "device_types": device_type,
            "mac": mac,
            "channel": channel,
            "rssi": rssi,
            "link": link,
            "input_bytes_read": input_bytes_read,
            "input_bitrate": input_bitrate,
            "demux_bytes_read": demux_bytes_read,
            "demux_bitrate": demux_bitrate,
            "discontinuities": discontinuities,
        }

    def extract_transition_data(self):
        """Flatten every captured stream-switch event into one row per transition,
        per device, for the 'Stream Transition Events' report table."""
        rows = []
        for eid, events in self.transitions.items():
            hostname = self.devices_data.get(eid, {}).get("hostname", eid)
            for i, ev in enumerate(events, start=1):
                pre = ev.get("pre_switch_stats") or {}
                switch_time = ev.get("switch_time")
                time_str = (
                    datetime.fromtimestamp(switch_time).strftime("%H:%M:%S")
                    if switch_time else "N/A"
                )
                rows.append({
                    "Device Name": hostname,
                    "Transition #": i,
                    "Time": time_str,
                    "From Stream": ev.get("from_stream", ""),
                    "To Stream": ev.get("to_stream", ""),
                    "Frames Displayed (pre-switch)": pre.get("frames_displayed", "0"),
                    "Frames Lost (pre-switch)": pre.get("frames_lost", "0"),
                    "Demux Bitrate (pre-switch)": pre.get("demux_bitrate", "0 kb/s"),
                })
        return rows

    def build_device_metrics_table(self, report_obj, device_info, metrics):
        """device_info: dict with Device Name/Type/Mac/Channel/RSSI keys.
        metrics: list of (metric, value) tuples."""
        rowspan_count = len(metrics)

        # first metric row with device info
        first_metric = metrics[0]
        html_rows = f"""
        <tr>
        <td rowspan="{rowspan_count}">{device_info.get('Device Name', '')}</td>
        <td rowspan="{rowspan_count}">{device_info.get('Device Type', '')}</td>
        <td rowspan="{rowspan_count}">{device_info.get('Mac Address', '')}</td>
        <td rowspan="{rowspan_count}">{device_info.get('Channel', '')}</td>
        <td rowspan="{rowspan_count}">{device_info.get('RSSI (dBm)', '')}</td>
        <td>{first_metric[0]}</td>
        <td>{first_metric[1]}</td>
        </tr>
        """

        # remaining metric rows without device info
        for metric in metrics[1:]:
            html_rows += f"""
        <tr>
        <td>{metric[0]}</td>
        <td>{metric[1]}</td>
        </tr>
        """

        # full table with headers
        table_html = f"""
        <table width='100%' border='1' cellpadding='4' cellspacing='0' style='border-collapse: collapse; border: 1px solid gray;'>
        <tr style='background-color: #f2f2f2;'>
            <th>Device Name</th>
            <th>Device Type</th>
            <th>Mac Address</th>
            <th>Channel</th>
            <th>RSSI (dBm)</th>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        {html_rows}
        </table>
        <br>
        """

        report_obj.html += table_html

    def print_run_summary(self):
        """One line per selected device: did it report, and did it actually receive
        anything? Reading the raw stats dict to answer that is too easy to get wrong."""
        logger.info("\n" + "=" * 72)
        logger.info("RUN SUMMARY")
        logger.info("=" * 72)

        for eid, device in self.devices_data.items():
            dtype = device.get("device type", "?")
            stats = self.stats.get(eid)

            if not stats:
                logger.warning(f"  {eid:<18} {dtype:<14} NO DATA -- never reported to the collector")
                continue

            if device.get("device type", "").lower() == "android":
                parsed = stats.get("parsed", {}) if isinstance(stats, dict) else {}
                rate = parsed.get("input_bitrate_kbps")
                fg = parsed.get("vlc_in_foreground")
                if rate:
                    logger.info(f"  {eid:<18} {dtype:<14} RECEIVING  ~{rate} kb/s on wlan0, "
                                f"VLC foreground={fg}")
                else:
                    logger.info(f"  {eid:<18} {dtype:<14} reported, but no throughput measured")
                continue

            def as_int(v):
                try:
                    return int(float(str(v).split()[0]))
                except Exception:
                    return 0

            read = as_int(stats.get("input_bytes_read", "0"))
            shown = as_int(stats.get("frames_displayed", "0"))
            disc = stats.get("discontinuities", "0")
            if read == 0:
                logger.warning(f"  {eid:<18} {dtype:<14} NO TRAFFIC -- 0 bytes read. The stream is not "
                               f"reaching this device.")
            elif shown == 0:
                logger.warning(f"  {eid:<18} {dtype:<14} PARTIAL -- {read} KiB read but 0 frames "
                               f"displayed ({disc} discontinuities). Too much loss to decode video.")
            else:
                logger.info(f"  {eid:<18} {dtype:<14} PLAYING -- {shown} frames displayed, "
                            f"{read} KiB read, {disc} discontinuities")

        if self.android_errors:
            logger.error("\n  Android automation errors:")
            for eid, msg in self.android_errors.items():
                logger.error(f"    {eid}: {msg}")

        logger.info("=" * 72 + "\n")

    def create_report(self):
        try:

            report = lf_report(_output_pdf='Vlc_Stremaing_Report',
                               _output_html='VLC_Streaming_Report.html',
                               _results_dir_name="VLC_Streaming_Report",
                               _path='')
            self.report_path_date_time = report.get_path_date_time()

            report.set_title("VLC Streaming Test")
            report.build_banner()

            report.set_table_title("Objective:")
            report.build_table_title()
            report.set_text("The Objective of the VLC media streaming test is to evaluate the performance and durability" +
                            " of video and audio streaming over Wi-Fi across multiple client platforms, including" +
                            "windows, Linux, macOS. By conducting this test, we aim to ensure successful stream" +
                            "initation, stable playback, and accurate collection of decoding statistics such as frames displayed, " +
                            "frames lost, buffer played and buffers lost. This helps assess the network's ability " +
                            "to support consistent and high-quality media streaming unser varying Wi-Fi consitions.")
            report.build_text_simple()

            report.set_table_title("Input Parameters:")
            report.build_table_title()

            test_setup_info = self.generate_test_setup_info()
            report.test_setup_table(test_setup_data=test_setup_info, value='Input Parameters')

            final_data = self.extract_data_for_reporting_for_laptop_clients()
            android_data = self.extract_data_for_reporting_for_android_clients()
            if len(final_data["hostnames"]) == 0:
                logger.info("No client data available for report generation.Continuing without client data.")
            else:
                report.set_graph_title("Video Frames per Device")
                report.build_graph_title()

                x_fig_size = 18
                y_fig_size = len(final_data["hostnames"]) * 1 + 4
                bar_graph_horizontal = lf_bar_graph_horizontal(
                    _data_set=[[int(float(x)) for x in final_data["frames_lost"]], [int(float(x)) for x in final_data["frames_displayed"]]],
                    _xaxis_name="No of Frames",
                    _yaxis_name="Device Name",
                    _yaxis_label=final_data["hostnames"],
                    _yaxis_categories=final_data["hostnames"],
                    _yaxis_step=1,
                    _yticks_font=8,
                    _bar_height=.20,
                    _show_bar_value=True,
                    _dpi=96,
                    _figsize=(x_fig_size, y_fig_size),
                    _graph_title="Video Frames Displayed/Lost per Device",
                    _graph_image_name="video_frames_per_device",
                    _label=["Frames Lost", "Frames Displayed"]
                )
                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                report.set_graph_image(graph_image)
                report.move_graph_image()
                report.build_graph()

                report.set_table_title("Test Results For Clients(Laptops)")
                report.build_table_title()
                report.set_text("The table below provides detailed information of both the Audio and Video Playback statistics of laptop device acting as clients.")
                report.build_text_simple()
                final_test_results = {

                    "Device Name": final_data["hostnames"],
                    "Device Type": final_data["device_types"],
                    "MAC Address": final_data["mac"],
                    "Channel": final_data["channel"],
                    "RSSI": final_data["rssi"],
                    "Link Rate": final_data["link"],
                    "Video Decoded ": final_data["video_decoded"],
                    "Frames Displayed ": final_data["frames_displayed"],
                    "Frames Lost ": final_data["frames_lost"],
                    "Audio Decoded ": final_data["audio_decoded"],
                    "Active Stream (last sample)": final_data["active_stream"],
                }

                test_results_df = pd.DataFrame(final_test_results)
                report.set_table_dataframe(test_results_df)
                report.build_table()
            if len(android_data["hostnames"]) == 0:
                logger.info("No Android client data available for report generation.Continuing without Android client data.")
            else:
                report.set_table_title("Test Results For Clients(Androids)")
                report.build_table_title()

                android_test_results = {

                    "Device Name": android_data["hostnames"],
                    "Device Type": android_data["device_types"],
                    "MAC Address": android_data["mac"],
                    "Channel": android_data["channel"],
                    "RSSI": android_data["rssi"],
                    "Link Rate": android_data["link"],
                    "Video Codec": android_data["video_codec"],
                    "Audio Codec": android_data["audio_codec"],
                    "Audio Channels": android_data["audio_channels"],
                    "Audio Sample Rate (Hz)": android_data["audio_sample_rate"],
                    "Demux Bitrate (kb/s)": android_data["demux_bitrate"],
                    "Input Bitrate (kb/s)": android_data["input_bitrate"],
                    "Framerate (fps)": android_data["framerate"],
                    "Possible Buffering Events": android_data["buffering_events"],
                    "VLC Playing": android_data["vlc_foreground"],
                }

                android_test_results_df = pd.DataFrame(android_test_results)
                android_test_results_df = android_test_results_df.fillna("None")

                report.set_table_dataframe(android_test_results_df)
                report.build_table()

                report.set_text("NOTE: VLC statistics on Android devices show audio parameters such as channel count and" +
                                " sample rate as zero due to Media Codec limitations in Android. This behavior is application-specific and " +
                                "does not indicate an issue with audio decoding or streaming quality. Unlike the laptop clients, the Android " +
                                "VLC app has no interface that reports exact frame-drop or buffer-loss counts, so \"Possible Buffering " +
                                "Events\" is a derived signal instead of a direct count: it increments whenever the on-screen playback " +
                                "position advances noticeably slower than real time between two polls, which is the closest available " +
                                "indicator of a stall or rebuffer on this platform. When Android runs in "
                                "playback-only mode (--android_simple), VLC's decode counters are not "
                                "reachable at all, so codec fields read N/A and the Input Bitrate column "
                                "instead reports bytes received on the phone's wlan0 interface, sampled "
                                "over adb. Note that figure covers all wlan0 traffic, not only this "
                                "multicast group -- during a dedicated streaming test the stream dominates, "
                                "but it is not a stream-isolated measurement.")
                report.build_text_simple()

                if self.android_errors:
                    error_lines = "; ".join(f"{eid}: {msg}" for eid, msg in self.android_errors.items())
                    report.set_text(f"NOTE: Android automation reported a failure on "
                                    f"{len(self.android_errors)} device(s) -- that's why their row(s) above show no "
                                    f"data rather than genuine playback stats: {error_lines}")
                    report.build_text_simple()
            if self.host_res:
                report.set_table_title("Test Result For Host")
                report.build_table_title()
                report_data = self.extract_data_for_reporting_for_host()

                for i in range(len(report_data["hostnames"])):
                    device_info = {
                        "Device Name": report_data["hostnames"][i],
                        "Device Type": report_data["device_types"][i],
                        "Mac Address": report_data["mac"][i],
                        "Channel": report_data["channel"][i],
                        "RSSI (dBm)": report_data["rssi"][i],
                    }
                    metrics = [
                        ("Input bytes read", report_data["input_bytes_read"][i]),
                        ("Input bitrate", report_data["input_bitrate"][i]),
                        ("Demux bytes read", report_data["demux_bytes_read"][i]),
                        ("Demux bitrate", report_data["demux_bitrate"][i]),
                        ("Discontinuities", report_data["discontinuities"][i]),
                    ]
                    self.build_device_metrics_table(report, device_info, metrics)

            transition_rows = self.extract_transition_data()
            if transition_rows:
                report.set_table_title("Stream Transition Events")
                report.build_table_title()
                report.set_text("The table below lists every automatic switch between the two configured " +
                                "multicast streams, together with the stats captured for the outgoing stream " +
                                "immediately before each switch.")
                report.build_text_simple()
                transitions_df = pd.DataFrame(transition_rows)
                report.set_table_dataframe(transitions_df)
                report.build_table()

            report.build_custom()
            report.build_footer()
            report.write_html()
            report.write_pdf()
        except Exception as e:
            logger.error(f"Error in create_report function {e}", exc_info=True)


SCRIPT_VERSION = "2026-09-11 (logging cleanup, help_summary, retries)"


def main():
    print(f"[VERSION] lf_interop_vlc.py {SCRIPT_VERSION}")
    print(f"[VERSION] running from: {os.path.abspath(__file__)}")

    help_summary = '''\
    VLC media streaming interoperability test: streams video from a host device
    to multiple Windows/Linux/macOS/Android clients over Wi-Fi multicast and
    reports per-device playback stats (frames, bitrate, buffering).
    '''

    parser = argparse.ArgumentParser(
        prog='lf_interop_vlc.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=r'''
NAME: lf_interop_vlc.py

PURPOSE:
lf_interop_vlc.py sets up a VLC media streaming interoperability test using LANforge.
It streams video -- from a clustered host device, from this LANforge machine itself
(--host_media), or from an external/WAN source (--external_source) -- to multiple
Windows/Linux/macOS/Android client devices over Wi-Fi multicast, and reports per-device
playback stats (frames displayed/lost, bitrate, buffering events).

EXAMPLE-1:
Stream a video from a specific clustered host resource to the selected clients:
python3 lf_interop_vlc.py --video_name 'C:\Users\Administrator\Downloads\sample.mp4' --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --host_res 1.13 --server_ip 192.168.0.57

EXAMPLE-2:
Same, but let the script pick the first non-Android selected device as host:
python3 lf_interop_vlc.py --video_name 'C:\Users\Administrator\Downloads\sample.mp4' --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --server_ip 192.168.0.57

EXAMPLE-3:
Run with every selected device as a client only (no host is started):
python3 lf_interop_vlc.py --duration 300 --mcast_port 1234 --mcast_addr 239.255.0.1 --server_ip 192.168.0.57

EXAMPLE-4:
Nokia/WAN-hosted external multicast source -- guarantees no clustered device is ever
picked as host, even if --host_res/--video_name are also passed:
python3 lf_interop_vlc.py --duration 300 --mcast_addr 239.255.0.1 --mcast_port 1234 --server_ip 192.168.0.57 --external_source

EXAMPLE-5:
Host two media files locally on this LANforge machine, rotating between them every 60s
(--host_media/--host_iface/--host_rotate), with laptop clients in simple playback mode
(--client_simple) and Android clients in simple/no-UI mode (--android_simple):
python3 lf_interop_vlc.py --mgr 192.168.207.75 --server_ip 192.168.207.75 \
    --mcast_addr 239.255.0.1 --mcast_port 1234 \
    --host_media "/home/lanforge/QA_TEST_VIDEO.mp4,/home/lanforge/testvideo.mp4" \
    --host_iface eth1 --host_rotate --client_script_dir /Users/lanforge --client_simple \
    --switch_mode time --switch_value 60 --external_source --android_simple --duration 120

SCRIPT_CLASSIFICATION: Test

NOTES:
1. Use './lf_interop_vlc.py --help' to see full command line usage and options.
2. --duration and --switch_value (in "time" switch mode) are both in seconds.
3. If --host_res/--video_name/devices aren't given, the script interactively lists
   available resources and prompts you to select which ones to use.
4. --external_source and --host_media are independent: --external_source only controls
   whether a clustered resource is picked as host; --host_media additionally makes this
   LANforge machine itself serve the stream, so the two are commonly used together.
        ''')
    optional = parser.add_argument_group('Optional arguments')

    optional.add_argument('--mgr',
                          type=str,
                          help='hostname where LANforge GUI is running',
                          default='localhost')
    optional.add_argument('--mcast_addr',
                          type=str,
                          help='IP for streaming video on host',
                          default='239.255.0.1')
    optional.add_argument('--mcast_port',
                          type=str,
                          help='Port for streaming video on host',
                          default='1234')
    optional.add_argument('--host_res',
                          type=str,
                          help='host resource id to broadcast the video the video',
                          default=None)
    optional.add_argument('--video_name',
                          type=str,
                          help='Video file name to strema on host',
                          default=None)
    optional.add_argument('--duration',
                          type=int,
                          help='duration of test',
                          default=60)
    optional.add_argument('--server_ip',
                          type=str,
                          help='server ip on which client will request',
                          default="0.0.0.0")
    optional.add_argument('--server_port',
                          type=int,
                          help='port of flask server',
                          default=5959)
    optional.add_argument('--extra_streams',
                          type=str,
                          help='Comma-separated ip:port pairs for additional streams beyond --mcast_addr/--mcast_port, '
                               'enables multi-stream switching for laptop (Windows/Linux/macOS) clients. '
                               'e.g. "239.255.0.2:1234,239.255.0.3:1234" -- 1 to 4 extra streams (5 total max).',
                          default=None)
    optional.add_argument('--mcast_addr2',
                          type=str,
                          help='[deprecated, still supported] second stream IP -- equivalent to putting it '
                               'first in --extra_streams',
                          default=None)
    optional.add_argument('--mcast_port2',
                          type=str,
                          help='[deprecated, still supported] second stream port',
                          default=None)
    optional.add_argument('--switch_mode',
                          type=str,
                          choices=['time', 'iteration'],
                          help='switch trigger: elapsed seconds ("time") or poll-cycle count ("iteration")',
                          default='time')
    optional.add_argument('--switch_value',
                          type=int,
                          help='seconds between switches (time mode) or poll cycles between switches (iteration mode)',
                          default=30)
    optional.add_argument('--external_source',
                          action="store_true",
                          help='Multicast source is external (Nokia-provided or WAN/LANforge-hosted) -- '
                               'no device in this run is ever selected as host, regardless of --host_res/--video_name')
    optional.add_argument('--adb_map',
                          type=str,
                          default=None,
                          help='Manual override when automatic ADB resource matching misses a device: '
                               'comma-separated ANDROID_RESOURCE_ID=ADB_ID pairs, e.g. '
                               '"1.11=1.4.HX98210001,1.1=1.4.ZY10020002"')
    optional.add_argument('--android_no_stats',
                          action="store_true",
                          help='Let Android clients play the stream without scraping the VLC Video '
                               'Information panel. The scraping gestures can disturb playback -- use '
                               'this when smooth Android playback matters more than per-device stats.')
    optional.add_argument('--android_simple',
                          action="store_true",
                          help='Android clients use playback-only mode: plain adb, no uiautomator2, '
                               'no UI gestures, no stats. The most reliable way to get the stream '
                               'actually playing on phones.')
    optional.add_argument('--host_media',
                          type=str,
                          default=None,
                          help='Comma-separated media files to host as multicast streams from THIS '
                               'machine, mapped in order onto the configured streams (first file to '
                               '--mcast_addr/--mcast_port, rest to --extra_streams). Starts the VLC '
                               'hosts, verifies traffic, and stops them at the end -- no separate '
                               'host_streams.bash run needed.')
    optional.add_argument('--host_iface',
                          type=str,
                          default=None,
                          help='Interface(s) to send the hosted multicast out of, e.g. eth1, or '
                               '"eth0,eth1" to serve client networks that no single interface '
                               'reaches. Overrides the routing table.')
    optional.add_argument('--host_gui',
                          action="store_true",
                          help='Show a VLC window for each hosted stream (needs a display; uses '
                               'DISPLAY=:1). Default is headless -- multicast output only.')
    optional.add_argument('--host_vb',
                          type=int,
                          default=None,
                          help='Transcode hosted video to this bitrate in kb/s (e.g. 800). Lower '
                               'bitrates survive multicast-over-WiFi far better.')
    optional.add_argument('--host_rotate',
                          action="store_true",
                          help='Host-side switching: play each --host_media file in turn on ONE '
                               'multicast group, stopping each source before starting the next. '
                               'Clients stay on a single URL the whole test, so this works on every '
                               'platform including Android. Interval comes from --switch_value.')
    optional.add_argument('--android_script',
                          type=str,
                          default=None,
                          help='Absolute path to vlc_android.py on the resource machine that has '
                               'the phones attached. Defaults to the copy beside this script. Set '
                               'this if that machine keeps them somewhere else.')
    optional.add_argument('--no_cleanup',
                          action="store_true",
                          help='Skip removing stale generic cross-connects before the run. Only use '
                               'this if something else on the LANforge is relying on existing '
                               'CX_generic-* cross-connects -- otherwise leftovers from earlier runs '
                               'make LANforge reject this run\'s commands.')
    optional.add_argument('--client_script_dir',
                          type=str,
                          default=None,
                          help='Directory containing ctvlc.py/ctvlc.bash ON THE LAPTOP CLIENTS, '
                               'e.g. /Users/lanforge. LANforge runs generic endpoints from its own '
                               'working directory, so without this a bare "bash ctvlc.bash" can '
                               'fail silently and the device reports nothing.')
    optional.add_argument('--client_simple',
                          action="store_true",
                          help='Laptop clients just play the stream -- no RC socket, no stats. '
                               'Equivalent to launching VLC by hand. Use when playback matters '
                               'more than per-device statistics (mirrors --android_simple).')
    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')
    parser.add_argument('--lf_logger_config_json', help='--lf_logger_config_json <json file>, json configuration of logger')

    args = parser.parse_args()

    if args.help_summary:
        logger.info(help_summary)
        sys.exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    if args.mgr is None:
        fetched_local_ip = socket.gethostbyname(socket.gethostname())
        logger.info(f"No --mgr provided. Using local IP address: {fetched_local_ip}")
        args.mgr = fetched_local_ip

    adb_map = {}
    if args.adb_map:
        for pair in args.adb_map.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if "=" not in pair:
                logger.warning(f"Ignoring malformed --adb_map entry (expected RES_ID=ADB_ID): {pair}")
                continue
            res_id, mapped_adb_id = pair.split("=", 1)
            adb_map[res_id.strip()] = mapped_adb_id.strip()

    extra_streams = []
    if args.mcast_addr2 and args.mcast_port2:
        extra_streams.append((args.mcast_addr2, args.mcast_port2))
    if args.extra_streams:
        for pair in args.extra_streams.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" not in pair:
                logger.error(f"Malformed --extra_streams entry (expected ip:port): {pair}")
                sys.exit(1)
            ip, port = pair.rsplit(":", 1)
            extra_streams.append((ip.strip(), port.strip()))
        if len(extra_streams) > 4:
            logger.error(f"{len(extra_streams)} extra streams given -- 4 extra (5 total) is the max supported.")
            sys.exit(1)

    host_media = []
    if args.host_media:
        host_media = [m.strip() for m in args.host_media.split(",") if m.strip()]

    vlc_stream_obj = VLCStream(
        manager_ip=args.mgr, mcast_addr=args.mcast_addr, mcast_port=args.mcast_port,
        video_name=args.video_name, host_res=args.host_res, duration=args.duration,
        fserver=args.server_ip, fport=args.server_port, extra_streams=extra_streams,
        switch_mode=args.switch_mode, switch_value=args.switch_value, external_source=args.external_source,
        adb_map=adb_map, android_no_stats=args.android_no_stats, android_simple=args.android_simple,
        host_media=host_media, host_iface=args.host_iface, host_gui=args.host_gui, host_vb=args.host_vb,
        host_rotate=args.host_rotate, android_script=args.android_script,
        client_script_dir=args.client_script_dir, client_simple=args.client_simple)
    vlc_stream_obj.preflight_checks()
    vlc_stream_obj.run_flask_server()
    try:
        # Start the local multicast hosts (if --host_media was given) before
        # the clients, so the streams are already live when clients subscribe.
        if args.host_rotate:
            if not host_media:
                logger.error("--host_rotate requires --host_media with at least one file.")
                sys.exit(1)
            if len(host_media) < 2:
                logger.warning("--host_rotate with a single media file: nothing to rotate to.")
            vlc_stream_obj.start_host_rotation()
        else:
            vlc_stream_obj.start_local_hosts()
        vlc_stream_obj.get_resource_data()
        if not args.no_cleanup:
            vlc_stream_obj.remove_stale_endpoints()
        vlc_stream_obj.create()
        vlc_stream_obj.start_generic()
        logger.info("starting test")
        logger.info(vlc_stream_obj.start_time)
        start = datetime.now()
        end = start + timedelta(seconds=args.duration)
        while datetime.now() < end:
            time.sleep(1)
        time.sleep(20)

        vlc_stream_obj.stop_generic()
        vlc_stream_obj.print_run_summary()
        vlc_stream_obj.create_report()
    finally:
        # Always stop the hosts we started, including on Ctrl+C or an error --
        # otherwise stale VLC processes hold the RC ports for the next run.
        vlc_stream_obj.stop_local_hosts()


if __name__ == "__main__":
    main()
